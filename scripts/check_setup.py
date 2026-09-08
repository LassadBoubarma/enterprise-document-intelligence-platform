import sys
import requests

print("Python:", sys.version.split()[0])
try:
    r = requests.get("http://localhost:11434/api/tags", timeout=2)
    print("Ollama:", "OK" if r.ok else f"HTTP {r.status_code}")
except Exception as exc:
    print("Ollama: not reachable")
    print("Reason:", exc)

print("\nIf Ollama is not reachable, start it and run:")
print("  ollama pull qwen3:4b")
