# main.py
import uvicorn
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from services.schema_discovery import SchemaDiscovery
from services.document_processor import DocumentProcessor
from services.query_engine import QueryEngine
from typing import List
import os

app = FastAPI(title="NLP Query Engine Demo")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global singleton for demo
ENGINE = {
    "connection_string": None,
    "schema": None,
    "query_engine": None,
    "doc_processor": DocumentProcessor(),
}

@app.post("/api/ingest/database")
async def ingest_database(connection_string: str = Form(...)):
    """Connect to DB and auto-discover schema"""
    try:
        sd = SchemaDiscovery(connection_string)
        schema = sd.analyze_database()
        ENGINE["connection_string"] = connection_string
        ENGINE["schema"] = schema
        qe = QueryEngine(connection_string)
        # Share the same doc processor instance so uploads persist across engine instances
        qe.doc_processor = ENGINE["doc_processor"]
        ENGINE["query_engine"] = qe
        return {"status": "ok", "schema": schema}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/schema")
async def get_schema():
    return ENGINE.get("schema") or {"error": "no schema discovered"}

@app.post("/api/ingest/documents")
async def ingest_documents(files: List[UploadFile] = File(...)):
    """Accept document uploads and index them"""
    if not files or len(files) == 0:
        raise HTTPException(status_code=400, detail="No files provided.")
    processed = []
    for f in files:
        content = await f.read()
        doc_id = ENGINE["doc_processor"].save_and_extract(content, f.filename)
        processed.append({"doc_id": doc_id, "filename": f.filename})
    # Build index after batch upload
    ENGINE["doc_processor"].build_index()
    # if query engine exists, ensure it references the same doc processor
    if ENGINE.get("query_engine"):
        ENGINE["query_engine"].doc_processor = ENGINE["doc_processor"]
    return {"status": "ok", "processed": processed, "total_indexed": len(ENGINE["doc_processor"].doc_ids)}

@app.get("/api/ingest/status")
async def ingest_status():
    return {"indexed": len(ENGINE["doc_processor"].doc_ids)}

@app.post("/api/query")
async def api_query(query: str = Form(...)):
    if not ENGINE.get("query_engine"):
        raise HTTPException(status_code=400, detail="No database connected. Use /api/ingest/database first.")
    res = ENGINE["query_engine"].process_query(query)
    return res

@app.get("/api/query/history")
async def query_history():
    if not ENGINE.get("query_engine"):
        return {"error": "no engine"}
    return ENGINE["query_engine"].history

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
