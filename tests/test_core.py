"""Unit tests for the parts that must never regress: chunking, access control, guard, cache, OCR repair."""

import numpy as np
import pytest

from policylens import config
from policylens.answer import extractive, should_refuse
from policylens.cache import SemanticCache
from policylens.chunking import chunk_blocks
from policylens.index import Index, tokenize
from policylens.models import Answer, Block
from policylens.parsers import repair_ocr_spacing, table_to_text
from policylens.retrieve import search
from policylens.service import Engine, detect_lang


class FakeEmbedder:
    """Deterministic bag of words hashing embedder so tests need no model download."""

    model_name = "fake"

    def embed(self, texts):
        out = np.zeros((len(texts), 128), dtype=np.float32)
        for i, t in enumerate(texts):
            for w in tokenize(t):
                out[i, sum(map(ord, w)) % 128] += 1.0
            out[i] /= np.linalg.norm(out[i]) or 1.0
        return out


def make_engine(tmp_path, **kw):
    docs = {
        "leave.txt": ("internal", "# Leave\nEmployees get 21 days of annual leave every year."),
        "pay.txt": ("hr_only", "# Pay\nThe maximum salary for Grade 3 is 150000 rupees."),
        "treasury.txt": ("finance_only", "# Treasury\nThe counterparty limit is 500 million rupees."),
    }
    e = Engine(index=Index(FakeEmbedder()), **kw)
    for name, (level, text) in docs.items():
        p = tmp_path / name
        p.write_text(text, encoding="utf-8")
        e.ingest(p, level, p.stem)
    return e


def test_table_to_text_keeps_row_self_describing():
    text = table_to_text([["Grade", "Hotel"], ["Grade 1", "9,000"], ["Grade 2", "12,000"]])
    assert text.splitlines()[0] == "Grade: Grade 1; Hotel: 9,000"


def test_section_chunks_never_cross_a_heading():
    blocks = [Block(1, "A", "text", "alpha " * 200), Block(1, "B", "text", "beta " * 50)]
    chunks = chunk_blocks(blocks, "d", "D", "public", "en", "section")
    assert all(("alpha" in c.text) != ("beta" in c.text) for c in chunks)


def test_table_stays_one_chunk_in_section_table_strategy():
    blocks = [Block(2, "T", "table", "Grade: 1; Hotel: 9\nGrade: 2; Hotel: 12")]
    chunks = chunk_blocks(blocks, "d", "D", "public", "en", "section_table")
    assert len(chunks) == 1 and chunks[0].kind == "table" and chunks[0].page == 2


def test_unknown_strategy_rejected():
    with pytest.raises(ValueError):
        chunk_blocks([], "d", "D", "public", "en", "nope")


def test_ocr_spacing_repair():
    fixed = repair_ocr_spacing("Thebranchvaultcashlimit isPKR25million")
    assert "branch vault cash limit" in fixed and "25 million" in fixed


def test_language_detection():
    assert detect_lang("annual leave") == "en"
    assert detect_lang("ہاٹ لائن کتنے گھنٹے دستیاب رہتی ہے") == "ur"


@pytest.mark.parametrize("role", list(config.ROLE_LEVELS))
def test_search_never_returns_chunks_above_clearance(tmp_path, role):
    e = make_engine(tmp_path)
    allowed = config.ROLE_LEVELS[role]
    for q in ("annual leave days", "maximum salary Grade 3", "counterparty limit"):
        for mode in ("dense", "bm25", "hybrid"):
            hits = search(e.index, q, allowed, 5, mode)
            assert all(h.chunk.access_level in allowed for h in hits)


def test_employee_cannot_see_restricted_answer_but_finance_can(tmp_path):
    e = make_engine(tmp_path, threshold=0.0)
    r = e.ask("What is the counterparty limit?", "employee")
    assert not any(c["doc_id"] == "treasury" for c in r["citations"])
    r = e.ask("What is the counterparty limit?", "finance")
    assert any(c["doc_id"] == "treasury" for c in r["citations"])


def test_cache_is_isolated_per_access_level(tmp_path):
    e = make_engine(tmp_path, threshold=0.0)
    e.ask("What is the counterparty limit?", "admin")  # admin answer is cached first
    r = e.ask("What is the counterparty limit?", "employee")
    assert not r["cached"]
    assert not any(c["doc_id"] == "treasury" for c in r["citations"])


def test_cache_hit_for_same_role():
    c, v = SemanticCache(), np.ones(4, dtype=np.float32) / 2
    c.put(frozenset({"public"}), v, Answer("x", False))
    assert c.get(frozenset({"public"}), v).text == "x"
    assert c.get(frozenset({"public", "hr_only"}), v) is None


def test_refusal_guard(tmp_path):
    e = make_engine(tmp_path)
    hits = search(e.index, "annual leave days", config.ROLE_LEVELS["employee"], 3)
    assert not should_refuse(hits, threshold=0.0)
    assert should_refuse(hits, threshold=1.01)
    assert should_refuse([], threshold=0.0)


def test_extractive_answer_cites_best_sentence(tmp_path):
    e = make_engine(tmp_path)
    hits = search(e.index, "How many days of annual leave?", config.ROLE_LEVELS["employee"], 3)
    ans = extractive("How many days of annual leave?", hits)
    assert "21 days" in ans.text and ans.citations[0]["doc_id"] == "leave"


def test_reingest_replaces_old_version(tmp_path):
    e = make_engine(tmp_path)
    p = tmp_path / "leave.txt"
    p.write_text("# Leave\nEmployees get 25 days of annual leave every year.", encoding="utf-8")
    e.ingest(p, "internal", "leave")
    texts = [c.text for c in e.index.chunks.values() if c.doc_id == "leave"]
    assert len(texts) == 1 and "25 days" in texts[0]


def test_unknown_access_level_rejected(tmp_path):
    e = make_engine(tmp_path)
    p = tmp_path / "x.txt"
    p.write_text("# X\nhello", encoding="utf-8")
    with pytest.raises(ValueError):
        e.ingest(p, "top_secret")
