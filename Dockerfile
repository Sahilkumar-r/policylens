FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 UV_LINK_MODE=copy
RUN pip install --no-cache-dir uv && apt-get update && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY src ./src
COPY static ./static
COPY data ./data
RUN uv sync --frozen --no-dev
# Pre-download the embedding model so the container starts offline.
RUN uv run python -c "from fastembed import TextEmbedding; from policylens import config; TextEmbedding(config.EMBED_MODEL)"
# Warm the embedding and OCR caches at build time, so the first request does not spend minutes on OCR.
RUN uv run python -c "import json; from pathlib import Path; from policylens.service import Engine; e = Engine(); [e.ingest(Path('data')/m['path'], m['access_level'], m['doc_id'], m['title']) for m in json.load(open('data/manifest.json', encoding='utf-8'))]"
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "policylens.api:app", "--host", "0.0.0.0", "--port", "8000"]
