from __future__ import annotations
import re
from typing import Sequence
import requests
from .models import SearchResult

DEFAULT_OLLAMA_URL = "http://localhost:11434"

def ollama_available(base_url: str = DEFAULT_OLLAMA_URL, timeout: float = 1.5) -> bool:
    try:
        r = requests.get(f"{base_url}/api/tags", timeout=timeout)
        return r.ok
    except requests.RequestException:
        return False

def _strip_thinking(text: str) -> str:
    return re.sub(r"<think>.*?</think>", "", text or "", flags=re.S | re.I).strip()

def build_grounded_prompt(question: str, results: Sequence[SearchResult]) -> str:
    evidence = []
    for i, result in enumerate(results, start=1):
        c = result.chunk
        evidence.append(f"[S{i}] {c.title} | source={c.source} | page={c.page}\n{c.text}")
    context = "\n\n".join(evidence)
    return f"""
You are an enterprise knowledge assistant.

RULES:
1. Answer ONLY from the supplied evidence.
2. Every factual claim must be supported by one or more citations such as [S1].
3. If the evidence is insufficient, say: "I could not find sufficient evidence in the accessible documents."
4. Do not use outside knowledge to fill gaps.
5. Do not reveal or infer content from documents that are not in the evidence.
6. Keep the answer concise and practical.

QUESTION:
{question}

EVIDENCE:
{context}

ANSWER:
""".strip()

def answer_with_ollama(
    question: str,
    results: Sequence[SearchResult],
    model: str = "qwen3:4b",
    base_url: str = DEFAULT_OLLAMA_URL,
    timeout: int = 180,
) -> str:
    if not results:
        return "I could not find sufficient evidence in the accessible documents."
    payload = {
        "model": model,
        "stream": False,
        "messages": [{"role": "user", "content": build_grounded_prompt(question, results)}],
        "options": {"temperature": 0.1},
    }
    r = requests.post(f"{base_url}/api/chat", json=payload, timeout=timeout)
    r.raise_for_status()
    text = r.json().get("message", {}).get("content", "")
    return _strip_thinking(text)
