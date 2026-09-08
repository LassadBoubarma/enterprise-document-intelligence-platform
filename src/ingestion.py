from __future__ import annotations
from pathlib import Path
from typing import BinaryIO
import csv, io
from pypdf import PdfReader
from .models import DocumentPage

SUPPORTED_TEXT_EXTENSIONS = {".txt", ".md"}

def read_pdf(file_obj: BinaryIO, document_id: str, title: str, source: str, allowed_roles: list[str]) -> list[DocumentPage]:
    reader = PdfReader(file_obj)
    pages: list[DocumentPage] = []
    for i, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:
            pages.append(DocumentPage(document_id, title, source, i, text, allowed_roles))
    return pages

def read_text_bytes(raw: bytes, document_id: str, title: str, source: str, allowed_roles: list[str]) -> list[DocumentPage]:
    text = raw.decode("utf-8", errors="replace").strip()
    if not text:
        return []
    return [DocumentPage(document_id, title, source, 1, text, allowed_roles)]

def read_uploaded_file(uploaded_file, document_id: str, title: str, allowed_roles: list[str]) -> list[DocumentPage]:
    name = getattr(uploaded_file, "name", title)
    suffix = Path(name).suffix.lower()
    raw = uploaded_file.getvalue()
    if suffix == ".pdf":
        return read_pdf(io.BytesIO(raw), document_id, title, name, allowed_roles)
    if suffix in SUPPORTED_TEXT_EXTENSIONS:
        return read_text_bytes(raw, document_id, title, name, allowed_roles)
    raise ValueError(f"Unsupported file type: {suffix}")

def load_sample_manifest(base_dir: str | Path) -> list[DocumentPage]:
    base_dir = Path(base_dir)
    pages: list[DocumentPage] = []
    with (base_dir / "manifest.csv").open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            file_path = base_dir / "sample_docs" / row["filename"]
            roles = [r.strip() for r in row["allowed_roles"].split("|") if r.strip()]
            pages.extend(read_text_bytes(
                file_path.read_bytes(),
                row["document_id"],
                row["title"],
                row["filename"],
                roles
            ))
    return pages
