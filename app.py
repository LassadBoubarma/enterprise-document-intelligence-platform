from __future__ import annotations
from pathlib import Path
import time, uuid
import pandas as pd
import streamlit as st

from src.audit import write_audit_event
from src.chunking import pages_to_chunks
from src.evaluator import evaluate_retriever, load_eval_questions
from src.ingestion import load_sample_manifest, read_uploaded_file
from src.llm import answer_with_ollama, ollama_available
from src.retrieval import HybridRetriever

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
AUDIT_LOG = DATA_DIR / "audit_log.jsonl"
ROLES = ["engineering", "security", "risk", "hr", "admin"]

st.set_page_config(page_title="Secure Enterprise RAG Platform", page_icon="🔐", layout="wide")
st.title("🔐 Secure Enterprise RAG & LLM Evaluation Platform")
st.caption("Open-source local LLM + permission-aware hybrid retrieval + reranking + citations + evaluation.")

if "retriever" not in st.session_state:
    st.session_state.retriever = None
if "indexed_source" not in st.session_state:
    st.session_state.indexed_source = None

with st.sidebar:
    st.header("Configuration")
    user_role = st.selectbox("User role", ROLES, index=0)
    model = st.selectbox("Local LLM", ["qwen3:4b", "qwen3:8b"], index=0)
    use_reranker = st.checkbox("Enable cross-encoder reranker", value=True)
    top_k = st.slider("Evidence passages", min_value=3, max_value=8, value=5)
    st.divider()
    if ollama_available():
        st.success("Ollama detected")
    else:
        st.warning("Ollama not detected — retrieval-only mode still works.")
    st.caption("The sample knowledge base is synthetic and demonstrates enterprise access control.")

tab_ask, tab_upload, tab_eval, tab_arch = st.tabs(["Ask", "Knowledge Base", "Evaluation", "Architecture"])

def build_retriever(pages, source_label: str):
    with st.spinner("Building embeddings, BM25 index and metadata..."):
        chunks = pages_to_chunks(pages)
        retriever = HybridRetriever(enable_reranker=use_reranker)
        retriever.build_index(chunks)
        st.session_state.retriever = retriever
        st.session_state.indexed_source = source_label
    return len(chunks)

with tab_upload:
    st.subheader("1. Load a knowledge base")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Synthetic enterprise demo")
        st.write("Loads internal-style Security, Incident Response, API and HR documents with different role permissions.")
        if st.button("Load sample knowledge base", type="primary"):
            pages = load_sample_manifest(DATA_DIR)
            count = build_retriever(pages, "synthetic sample knowledge base")
            st.success(f"Indexed {count} chunks.")
    with col2:
        st.markdown("#### Upload your own documents")
        uploaded = st.file_uploader("PDF, TXT or Markdown", type=["pdf", "txt", "md"], accept_multiple_files=True)
        allowed_roles = st.multiselect(
            "Roles allowed to access uploaded documents",
            ROLES[:-1],
            default=["engineering", "security", "risk"],
        )
        if st.button("Index uploaded documents"):
            if not uploaded:
                st.error("Upload at least one document.")
            elif not allowed_roles:
                st.error("Choose at least one allowed role.")
            else:
                pages = []
                for file in uploaded:
                    pages.extend(read_uploaded_file(
                        file,
                        document_id=f"upload-{uuid.uuid4().hex[:8]}",
                        title=file.name,
                        allowed_roles=allowed_roles,
                    ))
                count = build_retriever(pages, "uploaded documents")
                st.success(f"Indexed {count} chunks.")
    if st.session_state.retriever is not None:
        st.info(f"Current index: {st.session_state.indexed_source}")

with tab_ask:
    st.subheader("2. Ask a permission-aware question")
    if st.session_state.retriever is None:
        st.info("Open Knowledge Base and load the sample documents first.")
    else:
        examples = {
            "engineering": "What authentication is required for privileged API operations?",
            "security": "What should happen after a Sev-1 production security incident is detected?",
            "risk": "What is required when a third-party security exception is requested?",
            "hr": "Who is allowed to access employee compensation records?",
            "admin": "Summarise the access restrictions across the available policies.",
        }
        question = st.text_area("Question", value=examples[user_role], height=90)
        if st.button("Search and answer", type="primary"):
            start = time.perf_counter()
            results = st.session_state.retriever.search(question, user_role=user_role, top_k=top_k, candidate_k=20)
            retrieval_ms = int((time.perf_counter() - start) * 1000)
            if not results:
                st.error("No accessible evidence was found for this role.")
            else:
                has_ollama = ollama_available()
                if has_ollama:
                    with st.spinner(f"Generating with {model} locally through Ollama..."):
                        answer = answer_with_ollama(question, results, model=model)
                    st.markdown("### Answer")
                    st.write(answer)
                else:
                    st.markdown("### Retrieval-only mode")
                    st.write("Ollama is not running, so the system shows the evidence that would be sent to the local LLM.")
                rows = []
                for idx, r in enumerate(results, start=1):
                    rows.append({
                        "Source": f"S{idx}",
                        "Document": r.chunk.title,
                        "Page": r.chunk.page,
                        "Semantic": round(r.semantic_score, 4),
                        "BM25": round(r.bm25_score, 4),
                        "Hybrid": round(r.hybrid_score, 4),
                        "Rerank": round(r.rerank_score, 4) if r.rerank_score is not None else None,
                    })
                st.markdown("### Retrieval scores")
                st.dataframe(pd.DataFrame(rows), use_container_width=True)
                st.markdown("### Evidence")
                for idx, r in enumerate(results, start=1):
                    with st.expander(f"[S{idx}] {r.chunk.title} — page {r.chunk.page} (roles: {', '.join(r.chunk.allowed_roles)})"):
                        st.write(r.chunk.text)
                write_audit_event(
                    AUDIT_LOG,
                    role=user_role,
                    question=question,
                    sources=[f"{r.chunk.document_id}:p{r.chunk.page}" for r in results],
                    latency_ms=retrieval_ms,
                    model=model if has_ollama else "retrieval-only",
                )
                st.caption(f"Retrieval latency: {retrieval_ms} ms")

with tab_eval:
    st.subheader("3. Evaluate retrieval quality")
    st.write("The bundled benchmark measures Hit@1, Hit@3, Hit@5 and Mean Reciprocal Rank (MRR).")
    if st.session_state.retriever is None:
        st.info("Load the sample knowledge base first.")
    elif st.button("Run sample benchmark"):
        rows = load_eval_questions(DATA_DIR / "eval_questions.csv")
        metrics, details = evaluate_retriever(st.session_state.retriever, rows, top_k=5)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Hit@1", f"{metrics.hit_at_1:.0%}")
        c2.metric("Hit@3", f"{metrics.hit_at_3:.0%}")
        c3.metric("Hit@5", f"{metrics.hit_at_5:.0%}")
        c4.metric("MRR", f"{metrics.mrr:.3f}")
        view = [{
            "Question": x["question"],
            "Role": x["role"],
            "Expected": x["expected_document_id"],
            "Retrieved": " → ".join(x["ranked_document_ids"]),
            "Hit@1": x["hit@1"],
            "RR": round(x["rr"], 3),
        } for x in details]
        st.dataframe(pd.DataFrame(view), use_container_width=True)

with tab_arch:
    st.subheader("Architecture")
    st.code("""
User + role
   |
   +--> permission filter ----------------------------------+
   |                                                        |
Question                                                    |
   |                                                        |
   +--> SentenceTransformer embedding                       |
   +--> BM25 keyword search                                 |
   |                                                        |
   v                                                        |
Hybrid fusion                                               |
   |                                                        |
Top candidate chunks <--------------------------------------+
   |
Cross-encoder reranker
   |
Top evidence + page metadata
   |
   +--> visible citations
   |
   +--> local Qwen3 through Ollama
            |
       grounded answer
            |
       local audit log
""".strip(), language="text")
    st.markdown("""
**Security idea:** filtering happens before evidence reaches the LLM.

**Evaluation idea:** retrieval is measured separately from generation, so you can compare retrieval methods rather than assuming a fluent answer is correct.
""")
