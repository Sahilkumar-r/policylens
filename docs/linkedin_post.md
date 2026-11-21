# LinkedIn post draft (not posted)

I built a document assistant that refuses to leak, then spent most of my time measuring where it breaks.

PolicyLens reads scanned PDFs, tables, Urdu and English, cites the page it used, and checks the caller's role inside the search stores.

What I found:
- OCR dropped spaces, so keyword search found nothing. A spacing repair fixed it, but OCR still had a 42 percent word error rate on clean scans.
- My first benchmark gave every method the same score. It was too easy, so I added 190 pages of real SBP, FBR and HEC PDFs.
- One similarity cutoff cannot decide when to refuse. 37.5 percent of table questions were wrongly refused, and I show that failure in the demo.
- With no filter, 46 of 46 restricted questions pulled in a restricted chunk. With the filter, 0 across 824 role and question pairs.
- My LLM judge scored answers 88.9 percent correct. A plain string match said 98.4. The four answers I read were right, so I do not trust the judge yet.

Code, results and the failure analysis: https://github.com/Sahilkumar-r/policylens
Write up: https://sahilkumar.runs-on.dev/projects/policylens/

#RAG #LLM #DataScience #Pakistan
