# PolicyLens: PRD

## Problem
Companies want "chat with our documents". Demos work on clean Markdown. Real policy libraries are scanned
PDFs, tables, mixed Urdu and English, and some documents must only be visible to some staff. A wrong answer
or a leaked finance document is worse than no answer.

## Product
An assistant for a fictional company (Karachi based bank-like firm) over its HR and finance policy library
plus public regulator documents. It:
1. Ingests digital PDF, scanned PDF (OCR), DOCX, XLSX and HTML.
2. Answers with citations to document, page and section.
3. Refuses when the library does not contain the answer.
4. Enforces access levels at the vector store, so restricted text never enters retrieval or the prompt.

## Users
- Employee (public + internal), HR officer (adds hr_only), Finance officer (adds finance_only), Admin (all).

## Scope (v1)
Upload and index, hybrid search, optional reranker, cited answers, refusal guardrail, roles, query log,
semantic cache, evaluation harness, small web UI, Docker.

## Non-goals
Real SSO, multi-tenant billing, fine tuned models, GPU serving.

## Extra features beyond the guide
- **Cache isolation**: the semantic cache key includes the caller's allowed levels (cache leaks are a real bug class).
- **Review CLI** for eval labels so a human can confirm or fix each label and flag it reviewed.
- **Filter after retrieval comparison** that demonstrates the leak the guide warns about.

## Success criteria (targets, not results)
| Metric | Target |
|---|---|
| Restricted document leaks (retrieval and answer) | 0 over the security suite |
| Recall@5 on answerable questions | measured vs baselines, hybrid >= dense and >= BM25 |
| Refusal recall on unanswerable | >= 0.9 at precision >= 0.9 on validation |
| p95 query latency on CPU, offline mode | reported, no target |
| Everything reproducible | one command runs all evals |

## Target employers
Systems Limited, 10Pearls, Securiti, banks (HBL, Meezan, UBL), Folio3.
