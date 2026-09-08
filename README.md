# Secure Enterprise RAG & LLM Evaluation Platform

A portfolio-grade **enterprise Generative AI** project built around a **local open-weight LLM**, permission-aware Retrieval-Augmented Generation (RAG), hybrid search, reranking, citations, audit logging and retrieval evaluation.

> The bundled enterprise documents are entirely synthetic. They exist only to demonstrate the architecture.

## Why this is more than a "chat with PDF" demo

- **Local Qwen3 through Ollama**: no cloud LLM API is required.
- **Permission-aware retrieval**: inaccessible chunks are filtered before they can reach the LLM.
- **Hybrid retrieval**: SentenceTransformer semantic similarity + BM25 keyword search.
- **Cross-encoder reranking**: reorders the top retrieved candidates.
- **Grounded generation**: the LLM is instructed to answer only from retrieved evidence.
- **Page/source citations**: retrieved evidence is visible and labelled `[S1]`, `[S2]`, etc.
- **Retrieval evaluation**: Hit@1, Hit@3, Hit@5 and MRR on a synthetic benchmark.
- **Audit trail**: role, question, sources, model and retrieval latency are logged locally.
- **PDF/TXT/Markdown ingestion**.

## Architecture

```text
User + role
   |
   +--> permission filter ----------------------------------+
   |                                                        |
   v                                                        |
Question                                                    |
   |                                                        |
   +--> semantic embedding                                  |
   +--> BM25 keyword score                                  |
   |                                                        |
   v                                                        |
Hybrid score                                                |
   |                                                        |
   v                                                        |
Top candidates <--------------------------------------------+
   |
   v
Cross-encoder reranker
   |
   v
Top evidence + source/page metadata
   |
   +--> evidence shown in UI
   |
   +--> local Qwen3 through Ollama
            |
            v
      grounded cited answer
            |
            v
       local audit log
```

## Recommended model

Default:

```bash
ollama pull qwen3:4b
```

If your machine is stronger:

```bash
ollama pull qwen3:8b
```

## Windows quick start

### 1. Install Python

Python 3.11 is recommended.

```powershell
python --version
```

### 2. Install Ollama and pull the LLM

```powershell
ollama pull qwen3:4b
ollama run qwen3:4b
```

Type `/bye` to exit the test chat.

### 3. Create a Python environment

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

The first run downloads the embedding and reranker models too.

### 4. Start the app

```powershell
streamlit run app.py
```

Open:

```text
http://localhost:8501
```

### 5. Demo it

1. Open **Knowledge Base**.
2. Click **Load sample knowledge base**.
3. Go to **Ask**.
4. Select role `engineering`.
5. Ask `What authentication is required for privileged API operations?`
6. Change role to `hr`.
7. Ask `Who may access individual compensation records?`
8. Change back to `engineering` and ask the same HR question: the HR document should not be retrievable.
9. Open **Evaluation** and run the sample benchmark.

## macOS / Linux

```bash
ollama pull qwen3:4b
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

## Retrieval pipeline

### 1. Ingestion
PDF pages are extracted with PyPDF. TXT and Markdown are read directly.

### 2. Chunking
Text is split into overlapping chunks. Each chunk keeps document ID, source, page and allowed roles.

### 3. Embeddings
`sentence-transformers/all-MiniLM-L6-v2` maps each chunk and the user query to vectors.

### 4. BM25
BM25 finds exact lexical matches. This is useful for enterprise terms such as `OAuth 2.0`, `SEC-001` and `Sev-1`.

### 5. Hybrid fusion
The prototype combines normalised scores:

```text
hybrid = 0.70 * semantic + 0.30 * BM25
```

### 6. Permission filtering
Only chunks allowed for the current role are considered.

### 7. Reranking
`cross-encoder/ms-marco-MiniLM-L-6-v2` reads `(question, passage)` pairs and reorders the best candidates.

### 8. Local generation
The top evidence is sent to Qwen3 through Ollama on `localhost`. The prompt requires source citations and forbids filling gaps with outside knowledge.

## Evaluation

From the UI or:

```bash
python scripts/run_eval.py
```

Metrics:

- **Hit@1**: the expected source ranks first.
- **Hit@3 / Hit@5**: the expected source appears in the top K.
- **MRR**: rewards relevant sources appearing early.

Do **not** put benchmark numbers on your CV until you run the benchmark yourself and record the real output.

## Tests

```bash
pip install -r requirements-dev.txt
pytest -q
```

## Important files

```text
app.py                  Streamlit application
src/ingestion.py        PDF/TXT/Markdown ingestion
src/chunking.py         chunking + metadata
src/retrieval.py        embeddings + BM25 + hybrid fusion + reranking
src/llm.py              local Ollama/Qwen3 grounded generation
src/access_control.py   role-based retrieval filtering
src/evaluator.py        Hit@K + MRR
src/audit.py            JSONL audit log
data/sample_docs/       synthetic enterprise documents
data/eval_questions.csv synthetic retrieval benchmark
tests/                  unit tests
```

## Honest limitations

This is a strong **portfolio prototype**, not a production bank platform.

Current limitations:

- role selection is simulated instead of being linked to enterprise SSO;
- embeddings/index are stored in application memory;
- no encryption-at-rest layer;
- no OCR for scanned PDFs;
- no serious prompt-injection defence yet;
- no distributed vector database;
- evaluation currently measures retrieval quality rather than complete answer factuality.

These are useful interview talking points.

## Strong next upgrades

1. Qdrant or pgvector persistence
2. SSO/JWT and real RBAC/ABAC
3. prompt-injection detection
4. answer-faithfulness and citation evaluation
5. FastAPI backend + separate frontend
6. Docker and CI
7. OpenTelemetry tracing
8. structured extraction and tool calling
