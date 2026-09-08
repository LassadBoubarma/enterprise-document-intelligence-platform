from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
import json

def write_audit_event(path: str | Path, *, role: str, question: str, sources: list[str], latency_ms: int, model: str) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    event = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "role": role,
        "question": question,
        "sources": sources,
        "latency_ms": latency_ms,
        "model": model,
    }
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")
