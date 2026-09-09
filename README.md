# Enterprise Document Intelligence Platform

A secure document question-answering platform using Retrieval-Augmented Generation (RAG).

## Overview

This project implements a permission-aware document retrieval system that allows users to query enterprise knowledge bases while respecting access permissions.

The system combines:
- semantic search
- keyword retrieval
- document ranking
- local LLM generation
- source citations

## Architecture

User Question
        |
        v
Query Processing
        |
        v
Hybrid Retrieval
(BM25 + Embeddings)
        |
        v
Permission Filtering
        |
        v
Reranking
        |
        v
Local LLM Response
        |
        v
Answer + Evidence Sources


## Features

- Local LLM inference using Ollama
- Permission-aware retrieval
- Hybrid search
- Cross-encoder reranking
- Evidence citations
- Evaluation metrics
- Streamlit interface


## Technologies

Python  
Streamlit  
Ollama  
Sentence Transformers  
FAISS  
BM25  
PyTest


## Run locally

Create environment:

```bash
python -m venv .venv
