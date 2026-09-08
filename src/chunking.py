from __future__ import annotations
import re
from typing import List
from .models import Chunk, DocumentPage

def clean_text(text: str) -> str:
    text = (text or "").replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def chunk_text(text: str, chunk_size: int = 1100, overlap: int = 180) -> List[str]:
    text = clean_text(text)
    if not text:
        return []
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")
    chunks: List[str] = []
    start = 0
    n = len(text)
    while start < n:
        hard_end = min(start + chunk_size, n)
        end = hard_end
        if hard_end < n:
            window = text[start:hard_end]
            floor = int(len(window) * 0.75)
            candidates = [
                window.rfind(". ", floor),
                window.rfind("? ", floor),
                window.rfind("! ", floor),
                window.rfind("; ", floor),
                window.rfind("\n", floor),
            ]
            best = max(candidates)
            if best > 0:
                end = start + best + 1
        piece = text[start:end].strip()
        if piece:
            chunks.append(piece)
        if end >= n:
            break
        start = max(end - overlap, start + 1)
    return chunks

def pages_to_chunks(pages: list[DocumentPage], chunk_size: int = 1100, overlap: int = 180) -> list[Chunk]:
    output: list[Chunk] = []
    for page in pages:
        pieces = chunk_text(page.text, chunk_size=chunk_size, overlap=overlap)
        for i, piece in enumerate(pieces):
            output.append(Chunk(
                chunk_id=f"{page.document_id}-p{page.page}-c{i}",
                document_id=page.document_id,
                title=page.title,
                source=page.source,
                page=page.page,
                text=piece,
                allowed_roles=list(page.allowed_roles),
            ))
    return output
