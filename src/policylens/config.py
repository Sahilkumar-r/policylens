"""Constants shared across the package."""

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CACHE_DIR = ROOT / ".cache"

EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
RERANK_MODEL = os.getenv("RERANK_MODEL", "BAAI/bge-reranker-v2-m3-int8")

LEVELS = ("public", "internal", "hr_only", "finance_only")
ROLE_LEVELS = {
    "employee": frozenset({"public", "internal"}),
    "hr": frozenset({"public", "internal", "hr_only"}),
    "finance": frozenset({"public", "internal", "finance_only"}),
    "admin": frozenset(LEVELS),
}

# Refusal threshold on the top dense cosine; tuned on the validation split by `eval/run_evals.py refusal`.
REFUSAL_THRESHOLD = float(os.getenv("REFUSAL_THRESHOLD", "0.59"))
CACHE_SIMILARITY = 0.95

LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")
