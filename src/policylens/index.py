"""Vector index (Qdrant, payload filtered by access level) plus BM25 built only over allowed chunks."""

import hashlib
import pickle
import re

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client import models as qm

from . import config
from .models import Chunk

_TOKEN = re.compile(r"\w+", re.UNICODE)


def tokenize(text: str) -> list[str]:
    return _TOKEN.findall(text.lower())


class Embedder:
    """fastembed wrapper with a disk cache so repeated eval runs do not re-embed."""

    def __init__(self, model: str = config.EMBED_MODEL, cache: bool = True):
        self.model_name, self._model, self._use_cache = model, None, cache
        self._path = config.CACHE_DIR / "emb.pkl"
        self._cache: dict[str, np.ndarray] = {}
        if cache and self._path.exists():
            self._cache = pickle.loads(self._path.read_bytes())

    def _key(self, text: str) -> str:
        return hashlib.sha1((self.model_name + text).encode()).hexdigest()

    def embed(self, texts: list[str]) -> np.ndarray:
        missing = [t for t in dict.fromkeys(texts) if self._key(t) not in self._cache]
        if missing:
            if self._model is None:
                from fastembed import TextEmbedding

                self._model = TextEmbedding(self.model_name)
            for t, v in zip(missing, self._model.embed(missing), strict=True):
                self._cache[self._key(t)] = (v / np.linalg.norm(v)).astype(np.float32)
            if self._use_cache:
                config.CACHE_DIR.mkdir(exist_ok=True)
                self._path.write_bytes(pickle.dumps(self._cache))
        return np.stack([self._cache[self._key(t)] for t in texts])


class Index:
    COLLECTION = "chunks"

    def __init__(self, embedder: Embedder | None = None, url: str | None = None):
        self.emb = embedder or Embedder()
        self.client = QdrantClient(url=url) if url else QdrantClient(":memory:")
        self.chunks: dict[str, Chunk] = {}
        self.vecs: dict[str, np.ndarray] = {}
        self._pid: dict[int, str] = {}
        self._bm25: dict[frozenset, tuple] = {}
        self._next = 0
        dim = self.emb.embed(["dim probe"]).shape[1]
        self.client.recreate_collection(
            self.COLLECTION, vectors_config=qm.VectorParams(size=dim, distance=qm.Distance.COSINE)
        )

    def add(self, chunks: list[Chunk]) -> None:
        if not chunks:
            return
        vecs = self.emb.embed([c.text for c in chunks])
        points = []
        for c, v in zip(chunks, vecs, strict=True):
            self._pid[self._next] = c.id
            self.chunks[c.id], self.vecs[c.id] = c, v
            points.append(
                qm.PointStruct(
                    id=self._next,
                    vector=v.tolist(),
                    payload={"access_level": c.access_level, "doc_id": c.doc_id},
                )
            )
            self._next += 1
        self.client.upsert(self.COLLECTION, points)
        self._bm25.clear()

    def remove_doc(self, doc_id: str) -> int:
        """Incremental re-index: drop one document so it can be ingested again."""
        gone = [i for i, c in self.chunks.items() if c.doc_id == doc_id]
        self.client.delete(
            self.COLLECTION,
            qm.FilterSelector(
                filter=qm.Filter(must=[qm.FieldCondition(key="doc_id", match=qm.MatchValue(value=doc_id))])
            ),
        )
        for i in gone:
            del self.chunks[i], self.vecs[i]
        self._bm25.clear()
        return len(gone)

    def dense(self, qvec: np.ndarray, allowed: frozenset | None, k: int) -> list[tuple[str, float]]:
        """Top k by cosine. `allowed` is applied inside the vector store query (pre filter)."""
        flt = (
            None
            if allowed is None
            else qm.Filter(
                must=[qm.FieldCondition(key="access_level", match=qm.MatchAny(any=sorted(allowed)))]
            )
        )
        pts = self.client.query_points(self.COLLECTION, query=qvec.tolist(), query_filter=flt, limit=k).points
        return [(self._pid[p.id], p.score) for p in pts]

    def bm25(self, query: str, allowed: frozenset, k: int) -> list[tuple[str, float]]:
        """BM25 over allowed chunks only, so restricted text never influences scores or IDF."""
        if allowed not in self._bm25:
            ids = [i for i, c in self.chunks.items() if c.access_level in allowed]
            self._bm25[allowed] = BM25(ids, [tokenize(self.chunks[i].text) for i in ids]) if ids else None
        idx = self._bm25[allowed]
        return idx.top(tokenize(query), k) if idx else []


class BM25:
    def __init__(self, ids: list[str], docs: list[list[str]]):
        from rank_bm25 import BM25Okapi

        self.ids, self.model = ids, BM25Okapi(docs)

    def top(self, q: list[str], k: int) -> list[tuple[str, float]]:
        s = self.model.get_scores(q)
        order = np.argsort(-s)[:k]
        return [(self.ids[i], float(s[i])) for i in order if s[i] > 0]
