from dataclasses import dataclass, field


@dataclass
class Block:
    """A unit of parsed content before chunking."""

    page: int
    section: str
    kind: str  # "text" or "table"
    text: str


@dataclass
class Chunk:
    id: str
    doc_id: str
    title: str
    page: int
    section: str
    kind: str
    access_level: str
    lang: str
    text: str


@dataclass
class Hit:
    chunk: Chunk
    score: float  # fusion or rerank score used for ordering
    dense: float  # cosine between query and chunk, used by the refusal guard


@dataclass
class Answer:
    text: str
    refused: bool
    citations: list[dict] = field(default_factory=list)
    mode: str = "extractive"
    usage: dict = field(default_factory=dict)  # token counts reported by the provider, LLM mode only
