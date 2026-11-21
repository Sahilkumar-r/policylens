"""Three chunking strategies, compared in eval/ablate_chunking.py.

fixed          : ignore sections; sliding word windows over each page's text (tables flattened)
section        : windows inside a section only, so a chunk never crosses a heading
section_table  : like section, plus every table kept as its own chunk (split by rows only if too long)
"""

from .models import Block, Chunk

STRATEGIES = ("fixed", "section", "section_table")


def _windows(words: list[str], size: int, overlap: int) -> list[str]:
    if len(words) <= size:
        return [" ".join(words)]
    step = max(1, size - overlap)
    return [" ".join(words[i : i + size]) for i in range(0, len(words) - overlap, step)]


def _split_table(text: str, max_words: int) -> list[str]:
    out, cur, n = [], [], 0
    for row in text.splitlines():
        w = len(row.split())
        if cur and n + w > max_words:
            out.append("\n".join(cur))
            cur, n = [], 0
        cur.append(row)
        n += w
    if cur:
        out.append("\n".join(cur))
    return out


def chunk_blocks(
    blocks: list[Block],
    doc_id: str,
    title: str,
    access_level: str,
    lang: str,
    strategy: str = "section_table",
    size: int = 90,
    overlap: int = 15,
) -> list[Chunk]:
    if strategy not in STRATEGIES:
        raise ValueError(strategy)
    pieces: list[tuple[int, str, str, str]] = []  # page, section, kind, text
    if strategy == "fixed":
        by_page: dict[int, list[str]] = {}
        for b in blocks:  # tables are flattened into the page text and chunked like prose
            by_page.setdefault(b.page, []).append(b.text)
        for page, texts in by_page.items():
            for w in _windows(" ".join(texts).split(), size, overlap):
                pieces.append((page, "", "text", w))
    else:
        for b in blocks:
            if b.kind == "table" and strategy == "section_table":
                for t in _split_table(b.text, size + 40):
                    pieces.append((b.page, b.section, "table", t))
            else:
                for w in _windows(b.text.split(), size, overlap):
                    pieces.append((b.page, b.section, b.kind, w))
    return [
        Chunk(f"{doc_id}:{n}", doc_id, title, p, s, k, access_level, lang, t)
        for n, (p, s, k, t) in enumerate(pieces)
        if t.strip()
    ]
