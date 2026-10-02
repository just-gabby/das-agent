# DAS Writing Assistant

A local, offline AI writing assistant that helps drafting Design and Access
Statements and related planning documents, built for an internal team at a
housing development consultancy.

## What it does
- Runs entirely on-premise using Ollama (Llama 3.3 70B) — no cloud calls,
  no data leaves the local network
- Uses retrieval-augmented generation (RAG) with ChromaDB to match the
  firm's established tone and document structure
- Verifies every policy citation (NPPF, Local Plan) against an indexed,
  versioned policy library, rather than trusting the model's own claims
- Multi-user access via a Streamlit web app with authentication
- Automatic site-data lookups (nearest transport, nearest school) from
  open government datasets (NaPTAN, ONSPD, GIAS)

## Tech stack
Python, Ollama, ChromaDB, Streamlit, python-docx

## Note
This repository contains the application code only. Company-specific
content (precedent documents, policy library, configuration, and
credentials) has been excluded and is not included in this repository.