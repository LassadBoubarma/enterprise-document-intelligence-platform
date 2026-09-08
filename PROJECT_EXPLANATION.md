# Project explanation

## The business problem

A large company may have thousands of internal documents: policies, engineering standards, incident procedures, API documentation and risk guidance.

A general LLM does not automatically know the latest private documents. A naive chatbot can also leak information if it retrieves a document that the current user was not allowed to access.

This prototype demonstrates a more serious enterprise pattern:

1. ingest documents;
2. split them into searchable chunks;
3. keep permissions as metadata;
4. retrieve relevant chunks;
5. filter by user role;
6. rerank the best evidence;
7. give only that evidence to a local LLM;
8. require citations;
9. evaluate retrieval quality separately.

## RAG

RAG = Retrieval-Augmented Generation.

```text
Question
  -> retrieve relevant passages
  -> put those passages into the LLM prompt
  -> generate an answer from that context
```

The LLM is **not retrained**.

## Hybrid retrieval

### Semantic search
Embeddings represent meaning, so sentences with similar meaning can match even when the words differ.

### BM25
BM25 is keyword-oriented, so exact identifiers and technical terms can match strongly.

### Fusion
The prototype combines both:

```text
0.70 * semantic score + 0.30 * BM25 score
```

## Reranking

The retriever first creates a candidate set. A cross-encoder then scores each `(question, passage)` pair more carefully.

```text
all chunks
 -> top candidates from hybrid retrieval
 -> cross-encoder reranker
 -> top evidence
 -> LLM
```

## Permissions

Every document has `allowed_roles`.

Example:

```text
HR policy -> hr
API standard -> engineering, security
Incident guide -> engineering, security, risk
```

The code removes inaccessible chunks **before** they can be passed to the LLM.

This is a teaching example of RBAC, not production IAM.

## Local LLM

The app sends HTTP requests to Ollama:

```text
http://localhost:11434/api/chat
```

Default model:

```text
qwen3:4b
```

No OpenAI API key is required.

## Why citations matter

The LLM sees evidence labelled:

```text
[S1] API Standard ...
[S2] Incident Guide ...
```

The prompt requires factual claims to cite these labels.

The UI also exposes the exact retrieved passage and its source.

## Evaluation

The bundled benchmark contains:
- a question;
- a user role;
- the document expected to contain the evidence.

Metrics:
- Hit@1
- Hit@3
- Hit@5
- MRR

Example:

```text
Expected: API-001
Retrieved: INC-001 -> API-001 -> SEC-001
```

Then:
- Hit@1 = 0
- Hit@3 = 1
- reciprocal rank = 1/2

## Audit logging

Each question produces a local JSONL event containing:
- timestamp;
- role;
- question;
- retrieved sources;
- retrieval latency;
- LLM model.

This is not a compliance-grade audit system, but it demonstrates observability and traceability.

## Interview explanation

A concise explanation:

> I built a local enterprise RAG prototype using Qwen3 through Ollama. Documents are chunked with page and access metadata. Queries use a permission-aware hybrid retriever combining SentenceTransformer embeddings and BM25, followed by a cross-encoder reranker. Only the selected evidence is given to the LLM, which is prompted to answer with citations. I also created a benchmark measuring Hit@K and MRR so retrieval quality can be tested separately from the fluency of the LLM answer.

## What you can truthfully put on the CV after running it

**Secure Enterprise RAG & LLM Evaluation Platform**  
`Python · Qwen3 · Ollama · RAG · SentenceTransformers · BM25 · Cross-Encoder · Streamlit`

- Built a locally hosted enterprise knowledge assistant using Qwen3 and RAG, with permission-aware retrieval and source-grounded answers.
- Implemented hybrid semantic/BM25 retrieval and cross-encoder reranking with source citations for traceable document search.
- Added a retrieval benchmark measuring Hit@K and MRR, plus local audit logging of questions, sources and latency.

Do not add numeric benchmark results until you have run the benchmark yourself.

## What not to claim

Do not claim:
- production-grade security;
- zero hallucinations;
- fine-tuning;
- a vector database;
- OCR;
- real SSO;
- an agent system.

Those are future improvements.
