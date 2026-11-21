"""LLM plumbing: OpenRouter detection, retry on rate limits, citation parsing, demo read only mode."""

import importlib

import httpx
import pytest
from fastapi.testclient import TestClient
from test_core import make_engine

from policylens import answer, config
from policylens.api import app, get_engine
from policylens.retrieve import search


def reload_config(monkeypatch, **env):
    for k in ("LLM_API_KEY", "LLM_BASE_URL", "LLM_MODEL"):
        monkeypatch.delenv(k, raising=False)
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    return importlib.reload(config)


def test_openrouter_key_overrides_leftover_groq_settings(monkeypatch):
    c = reload_config(monkeypatch, LLM_API_KEY="sk-or-test", LLM_MODEL="llama-3.1-8b-instant")
    assert "openrouter.ai" in c.LLM_BASE_URL and "/" in c.LLM_MODEL
    reload_config(monkeypatch)  # restore defaults for later tests


def test_other_keys_keep_their_base_url(monkeypatch):
    c = reload_config(monkeypatch, LLM_API_KEY="abc", LLM_BASE_URL="https://example.test/v1")
    assert c.LLM_BASE_URL == "https://example.test/v1"
    reload_config(monkeypatch)


class FakeResponse:
    def __init__(self, status, body=None):
        self.status_code, self._body = status, body or {}
        self.request = httpx.Request("POST", "https://x.test")

    def json(self):
        return self._body

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError("bad", request=self.request, response=self)


def test_chat_retries_rate_limits_then_succeeds(monkeypatch):
    ok = FakeResponse(200, {"choices": [{"message": {"content": "hello"}}], "usage": {"total_tokens": 7}})
    calls = iter([FakeResponse(429), FakeResponse(429), ok])
    monkeypatch.setattr(answer.httpx, "post", lambda *a, **k: next(calls))
    monkeypatch.setattr(answer.time, "sleep", lambda s: None)
    text, usage = answer.chat("m", [{"role": "user", "content": "hi"}])
    assert text == "hello" and usage["total_tokens"] == 7


def test_chat_gives_up_after_retries(monkeypatch):
    monkeypatch.setattr(answer.httpx, "post", lambda *a, **k: FakeResponse(429))
    monkeypatch.setattr(answer.time, "sleep", lambda s: None)
    with pytest.raises(httpx.HTTPError):
        answer.chat("m", [], tries=2)


def test_generate_falls_back_to_extractive_when_llm_is_down(monkeypatch, tmp_path):
    e = make_engine(tmp_path)
    hits = search(e.index, "annual leave days", config.ROLE_LEVELS["employee"], 3)

    def down(question, hits):
        raise httpx.HTTPError("down")

    monkeypatch.setattr(answer, "llm_answer", down)
    assert answer.generate("annual leave days", hits, use_llm=True).mode == "extractive"


def test_llm_answer_keeps_only_valid_citations(monkeypatch, tmp_path):
    e = make_engine(tmp_path)
    hits = search(e.index, "annual leave days", config.ROLE_LEVELS["employee"], 2)
    monkeypatch.setattr(answer, "chat", lambda *a, **k: ("21 days [1] and a bogus [9]", {"total_tokens": 3}))
    ans = answer.llm_answer("annual leave days", hits)
    assert [c["n"] for c in ans.citations] == [1] and ans.usage["total_tokens"] == 3


def test_demo_readonly_blocks_uploads(monkeypatch, tmp_path):
    engine = make_engine(tmp_path)
    app.dependency_overrides[get_engine] = lambda: engine
    monkeypatch.setenv("DEMO_READONLY", "1")
    files = {"file": ("a.txt", b"# A\nhello", "text/plain")}
    r = TestClient(app).post(
        "/ingest",
        files=files,
        data={"access_level": "public"},
        headers={"Authorization": "Bearer demo-admin"},
    )
    app.dependency_overrides.clear()
    assert r.status_code == 403 and "public demo" in r.json()["detail"]
