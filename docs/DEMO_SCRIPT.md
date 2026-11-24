# Two minute demo video script

Record the screen with the app running (`uv run uvicorn policylens.api:app`). Without `LLM_API_KEY` the answers are
extractive, which is what the public demo uses. Keep the failure case in: it is what makes the rest believable.

| Time | Show | Say |
|---|---|---|
| 0:00 to 0:15 | The page, role set to Employee | "Company document assistants fail on scans, tables, and files some people must not see. PolicyLens is a document assistant built for that. I measured where it breaks." |
| 0:15 to 0:35 | Ask: `How many days of paid annual leave do permanent employees get?` | "It answers with the document, page and section. Here it is the HR leave policy, page 1." |
| 0:35 to 0:55 | Same role, ask: `What is the single transaction approval limit for the CFO?` | "That is in a finance only document. The employee gets a refusal, and the document is never retrieved. The role filter runs inside the vector store, so it cannot leak." |
| 0:55 to 1:15 | Switch to Finance officer, ask: `What is the net open foreign exchange position limit?` | "The finance officer gets the answer from a scanned PDF. OCR read it, and I had to repair dropped spaces to make search work." |
| 1:15 to 1:40 | Switch to Employee, ask: `What is the daily meal allowance for Grade 4?` | "Here is a failure. The answer is in a table the employee may read, and the system still refuses. 37.5 percent of table questions were refused, because one similarity cutoff cannot tell near misses from answers." |
| 1:40 to 1:55 | Open the README results tables | "Recall at 5 ranges from 92 to 100 percent by method. Zero leaks across 824 role and question pairs, and a deliberately buggy cache leaked 45 of 46, so the test can fail." |
| 1:55 to 2:00 | The repo page | "Code, tests, evals and failure analysis are on GitHub." |

Notes:
- The CFO question as Finance officer answers correctly now, so it is not the failure to show. The Grade 4 meal allowance question is refused every time (eval/results/failures.json, a036).
- The video built from this script is `docs/demo/policylens-demo.mp4`.
- Record at 1080p, 100 percent zoom, no notifications. Upload as unlisted on YouTube or Loom and add the link to the README.
