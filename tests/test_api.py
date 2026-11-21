"""API tests with a fake embedder so no model is downloaded."""

import pytest
from fastapi.testclient import TestClient
from test_core import make_engine

from policylens.api import app, get_engine


@pytest.fixture
def client(tmp_path):
    engine = make_engine(tmp_path, threshold=0.0)
    app.dependency_overrides[get_engine] = lambda: engine
    yield TestClient(app)
    app.dependency_overrides.clear()


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_requires_known_token(client):
    assert client.post("/ask", json={"question": "annual leave?"}).status_code == 401
    assert client.post("/ask", json={"question": "annual leave?"}, headers=auth("nope")).status_code == 401


def test_ask_returns_citation(client):
    r = client.post(
        "/ask", json={"question": "How many days of annual leave?"}, headers=auth("demo-employee")
    )
    assert r.status_code == 200 and r.json()["citations"][0]["doc_id"] == "leave"


def test_documents_list_respects_role(client):
    emp = {d["doc_id"] for d in client.get("/documents", headers=auth("demo-employee")).json()}
    fin = {d["doc_id"] for d in client.get("/documents", headers=auth("demo-finance")).json()}
    assert emp == {"leave"} and fin == {"leave", "treasury"}


def test_only_admin_can_ingest_or_read_logs(client):
    files = {"file": ("a.txt", b"# A\nhello world", "text/plain")}
    assert (
        client.post(
            "/ingest", files=files, data={"access_level": "public"}, headers=auth("demo-hr")
        ).status_code
        == 403
    )
    assert client.get("/logs", headers=auth("demo-employee")).status_code == 403
    ok = client.post("/ingest", files=files, data={"access_level": "public"}, headers=auth("demo-admin"))
    assert ok.status_code == 200 and ok.json()["chunks"] == 1


def test_bad_access_level_rejected(client):
    files = {"file": ("a.txt", b"# A\nhello", "text/plain")}
    r = client.post("/ingest", files=files, data={"access_level": "secret"}, headers=auth("demo-admin"))
    assert r.status_code == 422


def test_question_length_validated(client):
    assert client.post("/ask", json={"question": "a"}, headers=auth("demo-employee")).status_code == 422
