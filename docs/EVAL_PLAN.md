# PolicyLens: evaluation plan

## Corpus
- **Synthetic internal library** generated from a structured facts file (`data/facts.yaml`). Every fact has a
  value, document, page and access level, so the ground truth is known by construction, not guessed.
  Rendered to digital PDF, table PDF, simulated scanned PDF (rasterised, noisy), DOCX, XLSX, HTML and Urdu text.
- **Public documents** (SBP, FBR, HEC and similar) downloaded as is. Their questions are written by reading the
  text; those labels are **AI written and flagged `reviewed: false`** until a human confirms them with the review CLI.

## Question set (target 120 or more)
Categories: answerable text, table based, scanned, Urdu or mixed, unanswerable, permission restricted.
Each item: `id, question, category, role, gold_doc, gold_page, gold_answer (string match), answerable, label_source, reviewed`.

## Splits
Questions are split 40 percent validation and 60 percent test by a fixed seed before any tuning.
Refusal threshold and chunk size are tuned on validation only. Test is run once per final configuration.

## Metrics
| Area | Metric |
|---|---|
| Parsing | character error rate and table cell accuracy on 20 hard pages with known text |
| Retrieval | Recall@5, MRR, by category |
| Answer | gold answer string contained in answer (offline); faithfulness and judge scores only when an LLM key is set, with judge vs manual agreement on a 50 sample |
| Refusal | precision and recall on unanswerable questions |
| Security | restricted chunk leaks in retrieval and in answers, over an attack suite (role swaps, prompt injection inside docs, cache cross talk) |
| Ops | latency p50 and p95, cost per 1,000 queries (LLM mode only) |

## Baselines and ablations
BM25 only, dense only, hybrid; hybrid plus reranker; chunking: fixed vs section vs section and table;
filter before retrieval vs after retrieval (shows the leak the guide warns about).

## Honesty rules
Result files in `eval/results/` carry date, commit, mode and n. Offline mode is labelled as such. Unrun items say "not run".
Failure analysis: categorise at least 20 wrong answers by cause.
