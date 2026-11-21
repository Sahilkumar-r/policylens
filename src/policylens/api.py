"""FastAPI app. Auth is a bearer token mapped to a role in SQLite; demo tokens are for local use only."""

import json
import os
import tempfile
from pathlib import Path

from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from . import config
from .service import Engine

ROOT = Path(__file__).resolve().parents[2]
app = FastAPI(title="PolicyLens", version="0.1.0")
_engine: Engine | None = None


def get_engine() -> Engine:
    """Build once: embed the demo library so the first request is not the slow one."""
    global _engine
    if _engine is None:
        _engine = Engine(use_reranker=os.getenv("USE_RERANKER") == "1")
        manifest = ROOT / "data" / "manifest.json"
        if manifest.exists() and os.getenv("SKIP_DEMO_CORPUS") != "1":
            for m in json.loads(manifest.read_text(encoding="utf-8")):
                _engine.ingest(ROOT / "data" / m["path"], m["access_level"], m["doc_id"], m["title"])
    return _engine


def current_user(authorization: str = Header(default=""), e: Engine = Depends(get_engine)) -> dict:
    user = e.store.user(authorization.removeprefix("Bearer ").strip())
    if not user:
        raise HTTPException(401, "unknown token")
    return user


class AskBody(BaseModel):
    question: str = Field(min_length=3, max_length=500)


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/")
def ui():
    return FileResponse(ROOT / "static" / "index.html")


@app.get("/me")
def me(user: dict = Depends(current_user)):
    return {**user, "levels": sorted(config.ROLE_LEVELS[user["role"]])}


@app.post("/ask")
def ask(body: AskBody, user: dict = Depends(current_user), e: Engine = Depends(get_engine)):
    return e.ask(body.question, user["role"], user["name"])


@app.get("/documents")
def documents(user: dict = Depends(current_user), e: Engine = Depends(get_engine)):
    allowed = config.ROLE_LEVELS[user["role"]]
    docs: dict[str, dict] = {}
    for c in e.index.chunks.values():
        if c.access_level in allowed:
            d = docs.setdefault(
                c.doc_id, dict(doc_id=c.doc_id, title=c.title, access_level=c.access_level, chunks=0)
            )
            d["chunks"] += 1
    return sorted(docs.values(), key=lambda d: d["doc_id"])


@app.post("/ingest")
async def ingest(
    file: UploadFile = File(...),
    access_level: str = Form(...),
    user: dict = Depends(current_user),
    e: Engine = Depends(get_engine),
):
    if user["role"] != "admin":
        raise HTTPException(403, "only admin can ingest documents")
    if access_level not in config.LEVELS:
        raise HTTPException(422, f"access_level must be one of {config.LEVELS}")
    suffix = Path(file.filename or "upload").suffix.lower()
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / f"{Path(file.filename or 'upload').stem}{suffix}"
        path.write_bytes(await file.read())
        try:
            n = e.ingest(path, access_level)
        except ValueError as err:
            raise HTTPException(422, str(err)) from err
    return {"doc_id": path.stem, "chunks": n}


@app.get("/logs")
def logs(user: dict = Depends(current_user), e: Engine = Depends(get_engine)):
    if user["role"] != "admin":
        raise HTTPException(403, "admin only")
    return e.store.recent(50)
