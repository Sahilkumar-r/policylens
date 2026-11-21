# PolicyLens: interview notes (private)

## Why this approach over the alternatives
- Filtering by access level inside both stores is the only design where no later stage can forget to apply it. The
  eval shows the leak: with no filter, 46 of 46 restricted questions had a restricted chunk in the top 5.
- Hybrid search is justified by identifiers and numbers (BM25) plus paraphrases and Urdu (dense). My own data shows
  BM25 alone matching or beating hybrid on this corpus, so I say so instead of claiming hybrid always wins.
- OCR plus a spacing repair rather than a hosted OCR service: free, offline, measurable (42.4 and 51.7 percent WER).

## Biggest weakness and the fix
A single cosine threshold is a weak refusal guard. Correct short facts scored 0.48 to 0.53 while unrelated regulator
text scored 0.59 to 0.63. Fix: combine cosine with lexical coverage or the reranker score, and calibrate per category.
Table chunks are over refused (37.5 percent) because long chunks dilute the embedding; embed row groups instead.

## What changed at 100 times the data or users
Qdrant server with payload indexes, Postgres for users and logs, Redis for the cache with the same role keyed scheme,
a background ingest queue (OCR is about 18 seconds per scanned document), per tenant collections.
The BM25 per role index would move to a search engine with document level security.

## What it costs to run
Offline mode: CPU only, p50 about 32 ms per query on a laptop. LLM mode: not measured here (no key was available),
so no cost per 1,000 queries is claimed. The cross encoder reranker raises Recall@5 to 100 percent but takes about
10 seconds per query on CPU, which is why it is off by default.

## Questions I should expect
- Why not trust RAGAS alone? Not run here; I would report agreement with a 50 answer manual sample first.
- How do you know the eval is not just your own data? 14 of 22 documents are synthetic with known truth; the 8 real
  PDFs carry AI written labels flagged unreviewed. Say that plainly.
- What is the post filter versus pre filter difference? Equal recall here; the pre filter is a structural guarantee.
