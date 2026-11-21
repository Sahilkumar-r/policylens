"""Human review of AI written eval labels.

Shows each unreviewed question with its source sentence and gold answer. Press Enter to confirm, `e` to edit the
answer, `d` to drop the question, `q` to save and quit. Confirmed items get reviewed=true so reports can separate
human checked labels from AI written ones.   Usage: uv run python scripts/review_labels.py
"""

import json
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / "data" / "questions.json"


def main() -> None:
    qs = json.loads(PATH.read_text(encoding="utf-8"))
    keep, done = [], 0
    for q in qs:
        if q.get("reviewed") is not False:
            keep.append(q)
            continue
        print(
            f"\n[{q['id']}] {q['question']}\n  doc: {q['gold_doc']} p{q['gold_page']}\n  source: {q['evidence']}"
        )
        print(f"  gold answer: {q['gold_answer']}")
        cmd = input("  Enter=confirm, e=edit answer, d=drop, q=quit > ").strip().lower()
        if cmd == "q":
            keep.append(q)
            break
        if cmd == "d":
            continue
        if cmd == "e":
            q["gold_answer"] = input("  new answer: ").strip()
        q["reviewed"], done = True, done + 1
        keep.append(q)
    keep += qs[len(keep) :] if len(keep) < len(qs) and cmd == "q" else []
    PATH.write_text(json.dumps(keep, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"\nreviewed {done} labels, saved {PATH.name}")


if __name__ == "__main__":
    main()
