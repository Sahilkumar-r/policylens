# ADR 0001: multilingual MiniLM embeddings instead of bge-m3

**Status:** accepted

**Context.** The guide suggests bge-m3 for multilingual retrieval. The ONNX runtime used here (`fastembed`) does not
ship bge-m3. The only options that run on a CPU laptop without a GPU are
`paraphrase-multilingual-MiniLM-L12-v2` (0.22 GB, 384 dimensions, 50 languages including Urdu) and larger models
(multilingual-e5-large, 2.2 GB) that are slow to embed on CPU.

**Decision.** Use `paraphrase-multilingual-MiniLM-L12-v2`. A smoke test scored an Urdu question 0.55 against the
matching English sentence, so cross language retrieval works.

**Consequences.**
- The model reads at most 128 tokens, so chunks are about 90 words. Whole table chunks can exceed this and are
  truncated for the dense side only; BM25 still sees the full text. This is measured in the chunking comparison.
- Dense similarity scores are lower than for larger models, so the refusal threshold is tuned for this model.
- Swapping the model is one environment variable (`EMBED_MODEL`); the embedding cache is keyed by model name.
