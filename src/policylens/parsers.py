"""Parse PDF (digital and scanned), DOCX, XLSX, HTML and text into Blocks with page and section."""

import re
from pathlib import Path

from .models import Block

HEADING_RE = re.compile(r"^(?:\d+(?:\.\d+)*[.)]?\s+\S.{0,70}|(?:Section|Article|Chapter|Part)\s+\S.{0,60})$")
OCR_MIN_CHARS = 30
_ocr = None


def repair_ocr_spacing(text: str) -> str:
    """RapidOCR often drops spaces ('Thebranchvaultcashlimit isPKR25million'); this breaks BM25, embeddings
    and heading detection. Split long letter runs with a word frequency model; separate letters and digits."""
    import wordninja

    text = re.sub(r"[A-Za-z]{9,}", lambda m: " ".join(wordninja.split(m.group())), text)
    text = re.sub(r"(?<=[A-Za-z])(?=\d)|(?<=\d)(?=[A-Za-z])", " ", text)
    return re.sub(r"(?<=\d)\.(?=[A-Za-z])", ". ", text)


def ocr_image(png: bytes) -> str:
    """OCR one page image with RapidOCR (ONNX, CPU). Lines are ordered top to bottom."""
    global _ocr
    import hashlib
    import pickle

    from . import config

    path, key = config.CACHE_DIR / "ocr.pkl", hashlib.sha1(png).hexdigest()
    cache = pickle.loads(path.read_bytes()) if path.exists() else {}
    if key in cache:
        return repair_ocr_spacing(cache[key])
    if _ocr is None:
        from rapidocr_onnxruntime import RapidOCR

        _ocr = RapidOCR()
    result, _ = _ocr(png)
    rows = sorted(result or [], key=lambda r: (round(r[0][0][1] / 12), r[0][0][0]))
    text = "\n".join(r[1] for r in rows)
    config.CACHE_DIR.mkdir(exist_ok=True)
    cache[key] = text
    path.write_bytes(pickle.dumps(cache))
    return repair_ocr_spacing(text)


def table_to_text(rows: list[list]) -> str:
    """Render a table as 'Header: value; Header: value' lines so each row stays self describing."""
    rows = [[(c or "").strip().replace("\n", " ") for c in r] for r in rows if r and any(c for c in r)]
    if len(rows) < 2:
        return "\n".join(" | ".join(r) for r in rows)
    head, body = rows[0], rows[1:]
    return "\n".join("; ".join(f"{h}: {v}" for h, v in zip(head, r, strict=False)) for r in body)


def _sections(text: str, current: str) -> list[tuple[str, str]]:
    """Split page text into (section, text) parts at heading lines."""
    parts, buf = [], []
    for line in text.splitlines():
        s = line.strip()
        if s and HEADING_RE.match(s) and not s.endswith("."):
            if buf:
                parts.append((current, "\n".join(buf)))
            current, buf = s, []
        elif s:
            buf.append(s)
    if buf:
        parts.append((current, "\n".join(buf)))
    return parts


def parse_pdf(path: Path, ocr: bool = True, tables: bool = True) -> list[Block]:
    import fitz
    import pdfplumber

    blocks, section = [], ""
    doc = fitz.open(path)
    plumber = pdfplumber.open(path) if tables else None
    for i, page in enumerate(doc, start=1):
        text = page.get_text()
        if ocr and len(text.strip()) < OCR_MIN_CHARS:
            text = ocr_image(page.get_pixmap(dpi=200).tobytes("png"))
        tables_found = plumber.pages[i - 1].extract_tables() if plumber else []
        cells = {(c or "").strip() for t in tables_found for r in t for c in r}
        # table cells are emitted once, as a table block, not again as prose
        text = "\n".join(ln for ln in text.splitlines() if ln.strip() not in cells)
        for sec, body in _sections(text, section):
            section = sec
            blocks.append(Block(i, sec, "text", body))
        if plumber:
            for t in tables_found:
                tt = table_to_text(t)
                if tt:
                    blocks.append(Block(i, section, "table", tt))
    return blocks


def parse_docx(path: Path) -> list[Block]:
    import docx

    d, blocks, section, buf = docx.Document(path), [], "", []
    for p in d.paragraphs:
        if p.style.name.startswith("Heading"):
            if buf:
                blocks.append(Block(1, section, "text", "\n".join(buf)))
            section, buf = p.text.strip(), []
        elif p.text.strip():
            buf.append(p.text.strip())
    if buf:
        blocks.append(Block(1, section, "text", "\n".join(buf)))
    for t in d.tables:
        blocks.append(Block(1, section, "table", table_to_text([[c.text for c in r.cells] for r in t.rows])))
    return blocks


def parse_xlsx(path: Path) -> list[Block]:
    import openpyxl

    wb, blocks = openpyxl.load_workbook(path, data_only=True), []
    for n, ws in enumerate(wb.worksheets, start=1):
        rows = [["" if c is None else str(c) for c in r] for r in ws.iter_rows(values_only=True)]
        if rows:
            blocks.append(Block(n, ws.title, "table", table_to_text(rows)))
    return blocks


def parse_html(path: Path) -> list[Block]:
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    blocks, section, buf = [], "", []
    for tag in soup.find_all(["h1", "h2", "h3", "p", "li", "table"]):
        if tag.name in ("h1", "h2", "h3"):
            if buf:
                blocks.append(Block(1, section, "text", "\n".join(buf)))
            section, buf = tag.get_text(" ", strip=True), []
        elif tag.name == "table":
            rows = [
                [c.get_text(" ", strip=True) for c in r.find_all(["th", "td"])] for r in tag.find_all("tr")
            ]
            blocks.append(Block(1, section, "table", table_to_text(rows)))
        elif tag.find_parent("table") is None and tag.get_text(strip=True):
            buf.append(tag.get_text(" ", strip=True))
    if buf:
        blocks.append(Block(1, section, "text", "\n".join(buf)))
    return blocks


def parse_text(path: Path) -> list[Block]:
    blocks, section, buf = [], "", []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("#"):
            if buf:
                blocks.append(Block(1, section, "text", "\n".join(buf)))
            section, buf = line.lstrip("# ").strip(), []
        elif line.strip():
            buf.append(line.strip())
    if buf:
        blocks.append(Block(1, section, "text", "\n".join(buf)))
    return blocks


def parse(path: str | Path, tables: bool = True, ocr: bool = True) -> list[Block]:
    path = Path(path)
    ext = path.suffix.lower()
    fn = {
        ".pdf": parse_pdf,
        ".docx": parse_docx,
        ".xlsx": parse_xlsx,
        ".html": parse_html,
        ".htm": parse_html,
        ".txt": parse_text,
        ".md": parse_text,
    }.get(ext)
    if fn is None:
        raise ValueError(f"unsupported file type: {ext}")
    return fn(path, ocr=ocr, tables=tables) if fn is parse_pdf else fn(path)
