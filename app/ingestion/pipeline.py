"""Document ingestion for safe demo JSON and plain-text due-diligence materials."""
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from app.models import DocumentChunk

DEFAULT_CHUNK_SIZE = 900
DEFAULT_OVERLAP = 120


def _chunk_text(text: str, size: int = DEFAULT_CHUNK_SIZE, overlap: int = DEFAULT_OVERLAP) -> list[str]:
    cleaned = re.sub(r"\s+", " ", text).strip()
    if not cleaned:
        return []
    result: list[str] = []
    start = 0
    while start < len(cleaned):
        end = min(len(cleaned), start + size)
        if end < len(cleaned):
            boundary = cleaned.rfind(" ", start, end)
            if boundary > start + size // 2:
                end = boundary
        result.append(cleaned[start:end].strip())
        if end >= len(cleaned):
            break
        start = max(end - overlap, start + 1)
    return result


def ingest_text(path: Path, *, document_type: str = "document", date: str | None = None) -> list[DocumentChunk]:
    text = path.read_text(encoding="utf-8")
    document_id = hashlib.sha256(str(path).encode()).hexdigest()[:16]
    chunks = _chunk_text(text)
    return [DocumentChunk(
        chunk_id=f"{document_id}-{index}", text=chunk, document_id=document_id,
        document_name=path.name, document_type=document_type, page_number=index + 1,
        section="Document text", source=str(path), date=date,
    ) for index, chunk in enumerate(chunks)]


def ingest_case(path: Path) -> list[DocumentChunk]:
    """Turn the existing case JSON source register into traceable evidence chunks."""
    case: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    chunks: list[DocumentChunk] = []
    for source in case.get("sources", []):
        document_id = str(source.get("id", "unknown-source"))
        document_name = str(source.get("title", source.get("id", "Untitled source")))
        base = [str(source.get("summary", ""))]
        for assertion in source.get("assertions", []):
            base.append("; ".join(f"{key}: {value}" for key, value in assertion.items()))
        text = "\n".join(item for item in base if item.strip())
        for index, chunk in enumerate(_chunk_text(text)):
            chunks.append(DocumentChunk(
                chunk_id=f"{document_id}-{index}", text=chunk, document_id=document_id,
                document_name=document_name, document_type=str(source.get("source_type", "evidence")),
                page_number=source.get("page_number", index + 1), section=str(source.get("section", "Evidence")),
                source=str(source.get("origin", document_name)), date=str(source.get("date", "")) or None,
                metadata={"evidence_tier": int(source.get("evidence_tier", 3)), "topic": str(source.get("topic", "due diligence"))},
            ))
    return chunks
