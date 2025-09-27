# NLP Query Engine

This is a demo implementation of the assignment: **NLP Query Engine for Employee Data**.
It includes:
- FastAPI backend: schema discovery, document ingestion (embeddings + FAISS), query engine, caching.
- React frontend: DB connect, document uploader, query interface, results view.

## Prerequisites
- Python 3.8+
- Node.js (16+ recommended)
- pip, npm

## Backend setup
1. Open terminal:
```bash
cd project/backend
python -m venv venv
# Linux/macOS:
source venv/bin/activate
# Windows (PowerShell):
venv\Scripts\Activate.ps1
