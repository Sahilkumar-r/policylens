# ADR 0003: single node stack (Qdrant local mode, SQLite, in process cache)

**Status:** accepted, with a stated upgrade path

**Context.** The guide lists Qdrant server, Postgres, Redis and LiteLLM. This is a portfolio demo that has to run
with `docker compose up` on a laptop and on a free host.

**Decision.**
- Qdrant in local (in memory) mode. The client API and payload filters are identical; set `QDRANT_URL` style wiring in
  `Index(url=...)` to use a server.
- SQLite for users and the query log instead of Postgres.
- A process local semantic cache instead of Redis.
- A thin OpenAI compatible HTTP client instead of LiteLLM, because one provider at a time is enough.

**Consequences.** State is lost on restart (the demo library is re-ingested at startup; embeddings and OCR are cached
on disk). Two replicas would have separate caches and indexes. At 100 times the documents, move the index to a
Qdrant server, the log to Postgres and the cache to Redis keyed the same way.
