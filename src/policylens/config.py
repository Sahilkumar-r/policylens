"""Constants shared across the package."""

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CACHE_DIR = ROOT / ".cache"

# Read .env without a dependency. Real environment variables win; empty values are ignored.
_env = ROOT / ".env"
if _env.exists():
    for _line in _env.read_text(encoding="utf-8").splitlines():
        if "=" in _line and not _line.lstrip().startswith("#"):
            _k, _v = _line.split("=", 1)
            if _v.strip():
                os.environ.setdefault(_k.strip(), _v.strip())

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
# A different model family grades answers, so the generator never judges its own output.
LLM_JUDGE_MODEL = os.getenv("LLM_JUDGE_MODEL", "mistralai/mistral-small-3.2-24b-instruct")
OPENROUTER_URL = "https://openrouter.ai/api/v1"
if LLM_API_KEY.startswith("sk-or-") and "openrouter" not in LLM_BASE_URL:
    # An OpenRouter key was supplied with a leftover Groq URL or model id: use OpenRouter.
    LLM_BASE_URL = OPENROUTER_URL
    if "/" not in LLM_MODEL:
        LLM_MODEL = "meta-llama/llama-3.1-8b-instruct"
