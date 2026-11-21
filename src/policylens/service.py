"""Engine: ties parsing, chunking, index, retrieval, guard, cache and logging together."""

import re
import time
from pathlib import Path

from . import config
from .answer import REFUSAL, generate, should_refuse
from .cache import SemanticCache
from .chunking import chunk_blocks
from .index import Embedder, Index
from .models import Answer
from .parsers import parse
from .retrieve import Reranker, search
from .store import Store

_ARABIC = re.compile(r"[؀-ۿ]")


def detect_lang(text: str) -> str:
    letters = [c for c in text if c.isalpha()]
    ar = len(_ARABIC.findall(text))
    if not letters or ar == 0:
        return "en"
    return "ur" if ar / len(letters) > 0.6 else "mixed"


class Engine:
    def __init__(
        self,
        index: Index | None = None,
        store: Store | None = None,
        strategy: str = "section_table",
        mode: str = "hybrid",
        use_reranker: bool = False,
        threshold: float = config.REFUSAL_THRESHOLD,
        use_llm: bool | None = None,
        k: int = 5,
    ):
        self.index = index or Index(Embedder())
        self.store = store or Store()
        self.cache = SemanticCache()
        self.reranker = Reranker() if use_reranker else None
        self.strategy, self.mode, self.threshold, self.use_llm, self.k = strategy, mode, threshold, use_llm, k

    def ingest(
        self, path: str | Path, access_level: str, doc_id: str | None = None, title: str | None = None
    ) -> int:
        if access_level not in config.LEVELS:
            raise ValueError(f"unknown access level: {access_level}")
        path = Path(path)
        doc_id = doc_id or path.stem
        self.index.remove_doc(doc_id)  # re-ingesting replaces the old version
        blocks = parse(
            path, tables=self.strategy == "section_table"
        )  # naive strategies skip table extraction
        chunks = chunk_blocks(
            blocks, doc_id, title or path.stem.replace("_", " "), access_level, "en", self.strategy
        )
        for c in chunks:
            c.lang = detect_lang(c.text)
        self.index.add(chunks)
        self.cache = SemanticCache()  # cached answers may now be stale
        return len(chunks)

    def ask(self, question: str, role: str, user: str = "anon") -> dict:
        t0, trace = time.perf_counter(), {}
        allowed = config.ROLE_LEVELS[role]
        qvec = self.index.emb.embed([question])[0]
        cached = self.cache.get(allowed, qvec)
        if cached:
            ans, hits = cached, []
        else:
            t = time.perf_counter()
            hits = search(self.index, question, allowed, self.k, self.mode, self.reranker, qvec=qvec)
            trace["retrieve_ms"] = round((time.perf_counter() - t) * 1000, 1)
            ans = (
                Answer(REFUSAL, True)
                if should_refuse(hits, self.threshold)
                else generate(question, hits, self.use_llm)
            )
            self.cache.put(allowed, qvec, ans)
        ms = round((time.perf_counter() - t0) * 1000, 1)
        docs = sorted({c["doc_id"] for c in ans.citations})
        self.store.log(user, role, question, ans.refused, bool(cached), ms, docs)
        return {
            "answer": ans.text,
            "refused": ans.refused,
            "citations": ans.citations,
            "mode": ans.mode,
            "usage": ans.usage,
            "cached": bool(cached),
            "latency_ms": ms,
            "trace": trace,
            "retrieved": [h.chunk.id for h in hits],
            "top_score": max((h.dense for h in hits), default=0.0),
        }
