"""Semantic cache keyed by the caller's allowed levels, so no role is served another role's answer."""

import numpy as np

from . import config
from .models import Answer


class SemanticCache:
    def __init__(self, threshold: float = config.CACHE_SIMILARITY):
        self.threshold = threshold
        self._items: list[tuple[frozenset, np.ndarray, Answer]] = []

    def get(self, allowed: frozenset, qvec: np.ndarray) -> Answer | None:
        for key, v, ans in self._items:
            if key == allowed and float(v @ qvec) >= self.threshold:
                return ans
        return None

    def put(self, allowed: frozenset, qvec: np.ndarray, ans: Answer) -> None:
        self._items.append((allowed, qvec, ans))
