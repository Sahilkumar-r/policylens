"""SQLite: users (token to role) and the query log. Postgres would replace this at scale."""

import json
import sqlite3
import time

DEMO_USERS = [
    ("demo-employee", "Ayesha (employee)", "employee"),
    ("demo-hr", "Bilal (HR)", "hr"),
    ("demo-finance", "Farah (finance)", "finance"),
    ("demo-admin", "Admin", "admin"),
]


class Store:
    def __init__(self, path: str = ":memory:"):
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.db.execute("CREATE TABLE IF NOT EXISTS users(token TEXT PRIMARY KEY, name TEXT, role TEXT)")
        self.db.execute("""CREATE TABLE IF NOT EXISTS logs(ts REAL, user TEXT, role TEXT, question TEXT,
            refused INT, cached INT, latency_ms REAL, doc_ids TEXT)""")
        self.db.executemany("INSERT OR IGNORE INTO users VALUES(?,?,?)", DEMO_USERS)
        self.db.commit()

    def user(self, token: str) -> dict | None:
        r = self.db.execute("SELECT name, role FROM users WHERE token=?", (token,)).fetchone()
        return {"name": r[0], "role": r[1]} if r else None

    def log(
        self, user: str, role: str, question: str, refused: bool, cached: bool, ms: float, docs: list[str]
    ):
        self.db.execute(
            "INSERT INTO logs VALUES(?,?,?,?,?,?,?,?)",
            (time.time(), user, role, question, int(refused), int(cached), ms, json.dumps(docs)),
        )
        self.db.commit()

    def recent(self, n: int = 50) -> list[dict]:
        cur = self.db.execute("SELECT * FROM logs ORDER BY ts DESC LIMIT ?", (n,))
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r, strict=True)) for r in cur.fetchall()]
