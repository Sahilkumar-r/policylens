"""Hybrid retrieval: access filter first, dense + BM25, reciprocal rank fusion, optional reranker."""

import numpy as np

from . import config
from .index import Index
from .models import Hit

MODES = ("dense", "bm25", "hybrid")


class Reranker:
    def __init__(self, model: str = config.RERANK_MODEL):
        self.model_name, self._m = model, None

    def scores(self, query: str, texts: list[str]) -> list[float]:
        if self._m is None:
            from fastembed.rerank.cross_encoder import TextCrossEncoder

            self._m = TextCrossEncoder(self.model_name)
        return [float(s) for s in self._m.rerank(query, texts)]


def rrf(rankings: list[list[str]], k: int = 60) -> list[tuple[str, float]]:
    score: dict[str, float] = {}
    for r in rankings:
        for rank, cid in enumerate(r):
            score[cid] = score.get(cid, 0.0) + 1.0 / (k + rank + 1)
    return sorted(score.items(), key=lambda x: -x[1])


def search(
    index: Index,
    query: str,
    allowed: frozenset,
    k: int = 5,
    mode: str = "hybrid",
    reranker: Reranker | None = None,
    pool: int = 20,
    qvec: np.ndarray | None = None,
    filter_stage: str = "pre",
) -> list[Hit]:
    """filter_stage: 'pre' (default, inside the stores), 'post' (filter after top k, ablation only),
    'none' (no filter, ablation only). Production always uses 'pre'."""
    qvec = index.emb.embed([query])[0] if qvec is None else qvec
    pre = allowed if filter_stage == "pre" else None
    dense = index.dense(qvec, pre, pool) if mode in ("dense", "hybrid") else []
    lex = (
        index.bm25(
            query,
            allowed if filter_stage == "pre" else frozenset({c.access_level for c in index.chunks.values()}),
            pool,
        )
        if mode in ("bm25", "hybrid")
        else []
    )
    fused = rrf([[c for c, _ in dense], [c for c, _ in lex]])
    ids = [c for c, _ in fused][: max(k, pool) if reranker else k]
    if filter_stage == "post":
        ids = [c for c in [c for c, _ in fused][:k] if index.chunks[c].access_level in allowed]
    scores = dict(fused)
    if reranker and ids:
        rr = reranker.scores(query, [index.chunks[c].text for c in ids])
        order = sorted(zip(ids, rr, strict=True), key=lambda x: -x[1])[:k]
        return [Hit(index.chunks[c], s, float(index.vecs[c] @ qvec)) for c, s in order]
    return [Hit(index.chunks[c], scores[c], float(index.vecs[c] @ qvec)) for c in ids]
