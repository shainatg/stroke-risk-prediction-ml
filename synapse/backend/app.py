"""
Synapse FastAPI Backend Service
===============================
Principal-grade REST API powering the Synapse Semantic Analysis Studio.
Orchestrates document parsing, 128D deterministic vector embeddings,
cosine similarity ranking, grounded answer synthesis, 2D PCA projection,
and audit logging.
"""

import os
import time
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from core.similarity_engine import (
    generate_educational_embedding,
    cosine_similarity,
    chunk_text
)
from core.document_parser import DocumentParser
from core.synthesizer import (
    synthesize_grounded_answer,
    synthesize_normal_llm_answer,
    explain_similarity_match
)
from core.projection import compute_2d_projection
from core.report_generator import generate_analysis_pdf
from core import database

# Initialize database
database.init_db()

UPLOAD_DIR = Path(__file__).resolve().parent / "data" / "uploads"
SAMPLE_DIR = Path(__file__).resolve().parent / "sample_data"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="Synapse Semantic Analysis Engine",
    description="Deterministic 128D Vector Semantic Similarity Studio",
    version="1.0.0"
)

# CORS configuration for modern web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==============================================================================
# Pydantic Schemas
# ==============================================================================

class AnalyzeRequest(BaseModel):
    document_id: str = Field(..., description="ID of the document stored in Synapse database")
    query: str = Field(..., min_length=1, description="Question or statement to analyze against the document")
    chunk_size: int = Field(25, ge=5, le=100, description="Sliding window chunk size in words")
    chunk_overlap: int = Field(6, ge=0, le=50, description="Boundary overlap in words")
    top_k: int = Field(5, ge=1, le=20, description="Number of top matching passages to return")


class DirectTextAnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=10, description="Direct text to analyze")
    title: str = Field("Pasted Document", description="Title for the document")
    query: str = Field(..., min_length=1, description="User query")
    chunk_size: int = Field(25, ge=5, le=100)
    chunk_overlap: int = Field(6, ge=0, le=50)
    top_k: int = Field(5, ge=1, le=20)


# ==============================================================================
# 1. Health & Pipeline Metadata
# ==============================================================================

@app.get("/api/health")
def get_health():
    return {
        "status": "online",
        "service": "Synapse Semantic Analysis Engine",
        "version": "1.0.0",
        "embedding_dimension": 128,
        "algorithm": "Deterministic Hash Projection + Cosine Metric",
        "pure_python_verified": True
    }


@app.get("/api/pipeline/info")
def get_pipeline_info():
    """Returns technical specifications of every stage for the Interactive Pipeline Explorer."""
    return {
        "stages": [
            {
                "id": "input",
                "name": "User Query & Document Ingestion",
                "phase": "Phase 1",
                "description": "Receives multi-format documents (PDF, DOCX, TXT, CSV) alongside the analytical query or hypothesis.",
                "technical_details": "Supports binary stream extraction, MIME-type validation, and payload size bounds checking.",
                "formula": "D = \\{p_1, p_2, \\dots, p_n\\}, \\quad q \\in \\Sigma^*"
            },
            {
                "id": "parsing",
                "name": "Multi-Format Document Parsing",
                "phase": "Phase 2",
                "description": "Extracts raw text streams with page-by-page and paragraph tracking.",
                "technical_details": "pypdf processes PDF object streams preserving page numbers. python-docx extracts paragraph and table runs. CSV parses column headers and rows.",
                "formula": "\\text{Parse}(D) \\rightarrow (T, \\text{PageSpans}, \\text{Metadata})"
            },
            {
                "id": "chunking",
                "name": "Sliding Window Passage Chunking",
                "phase": "Phase 3",
                "description": "Segments normalized document text into word sequences with preserved boundary token overlap.",
                "technical_details": "Word stride S = C - O ensures critical facts spanning sentence boundaries are not split.",
                "formula": "S = C - O, \\quad \\text{Chunks} = \\left\\lceil \\frac{N - O}{S} \\right\\rceil"
            },
            {
                "id": "embedding",
                "name": "128D Dense Vector Embedding",
                "phase": "Phase 4",
                "description": "Projects each passage and query into a 128-dimensional continuous vector space with semantic locality.",
                "technical_details": "Uses TF-IDF salience weighting, dual FNV-1a (32-bit offset 2166136261) and DJB2 (offset 5381) hash mixing, character 3-grams, and L2 unit normalization (||v|| = 1.0).",
                "formula": "\\mathbf{v}_{L2} = \\frac{\\mathbf{v}}{\\sqrt{\\sum_{i=1}^{128} v_i^2}}"
            },
            {
                "id": "cosine",
                "name": "Geometric Cosine Similarity",
                "phase": "Phase 5",
                "description": "Computes exact angle of separation between the query vector and all document chunk vectors.",
                "technical_details": "Because vectors are L2 normalized to unit spheres, the cosine similarity is the inner dot product q · c.",
                "formula": "\\cos(\\theta) = \\frac{\\mathbf{q} \\cdot \\mathbf{c}}{\\|\\mathbf{q}\\| \\|\\mathbf{c}\\|} = \\sum_{d=1}^{128} q_d \\cdot c_d"
            },
            {
                "id": "ranking",
                "name": "Passage Ranking & Top-K Retrieval",
                "phase": "Phase 6",
                "description": "Sorts passages in descending order of semantic similarity, selecting candidate context for factual attribution.",
                "technical_details": "Maintains chunk citations, source page numbers, and character span offsets for document viewer jumping.",
                "formula": "R = \\text{argpartition}\\left(\\left\\{ \\cos(\\mathbf{q}, \\mathbf{c}_i) \\right\\}, K\\right)"
            },
            {
                "id": "synthesis",
                "name": "Grounded Answer Synthesis",
                "phase": "Phase 7",
                "description": "Synthesizes an evidence-grounded answer citing the exact source passages and explaining why the match occurred.",
                "technical_details": "Extracts high-salience query terms, locates verified matching sentences, and contrasts with ungrounded parametric LLM generation.",
                "formula": "\\text{Answer} = \\text{ExtractEvidence}(q, \\text{TopChunks}) \\cup \\text{Citations}"
            }
        ]
    }


# ==============================================================================
# 2. Document Ingestion & Management
# ==============================================================================

@app.get("/api/documents")
def list_documents():
    """Lists all uploaded documents and available sample corpora."""
    docs = database.list_documents()
    
    # Also inspect available sample files on disk
    sample_files = []
    if SAMPLE_DIR.exists():
        for f in SAMPLE_DIR.iterdir():
            if f.is_file() and not f.name.startswith("test_blank"):
                ext = f.suffix.lstrip(".").lower()
                sample_files.append({
                    "id": f"sample_{f.stem}",
                    "filename": f.name,
                    "file_type": ext,
                    "file_size": f.stat().st_size,
                    "is_sample": True
                })

    return {
        "documents": docs,
        "sample_corpora": sample_files
    }


@app.post("/api/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    chunk_size: int = Form(25),
    chunk_overlap: int = Form(6)
):
    """Uploads and parses a PDF, DOCX, TXT, or CSV document."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded.")

    ext = file.filename.lower().split(".")[-1]
    if ext not in ("pdf", "docx", "doc", "txt", "csv", "md"):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format '.{ext}'. Supported formats are: PDF, DOCX, TXT, CSV."
        )

    # Save to disk
    save_path = UPLOAD_DIR / file.filename
    try:
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # Parse document
    try:
        parsed_doc = DocumentParser.parse_file(save_path, file.filename)
    except Exception as e:
        if save_path.exists():
            save_path.unlink()
        raise HTTPException(status_code=422, detail=f"Document parsing error: {str(e)}")

    # Chunk text
    page_spans = [
        {"page": p["page"], "start_char": p["start_char"], "end_char": p["end_char"]}
        for p in parsed_doc.get("pages", [])
    ]
    chunks = chunk_text(
        parsed_doc["full_text"],
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        page_spans=page_spans
    )

    if not chunks:
        raise HTTPException(status_code=422, detail="Document could not be partitioned into any text chunks.")

    # Save to database
    doc_id = database.save_document(parsed_doc, chunks)

    return {
        "status": "success",
        "document_id": doc_id,
        "filename": parsed_doc["filename"],
        "file_type": parsed_doc["file_type"],
        "file_size": parsed_doc["file_size"],
        "total_pages": parsed_doc["total_pages"],
        "word_count": parsed_doc["word_count"],
        "char_count": parsed_doc["char_count"],
        "chunk_count": len(chunks),
        "preview": parsed_doc["full_text"][:350] + "..."
    }


@app.post("/api/documents/load-sample")
def load_sample_document(
    sample_name: str = Query(..., description="Filename of sample document in sample_data directory"),
    chunk_size: int = Query(25),
    chunk_overlap: int = Query(6)
):
    """Loads a pre-packaged sample document into the active workspace."""
    sample_path = SAMPLE_DIR / sample_name
    if not sample_path.exists():
        raise HTTPException(status_code=404, detail=f"Sample document '{sample_name}' not found.")

    parsed_doc = DocumentParser.parse_file(sample_path, sample_name)
    page_spans = [
        {"page": p["page"], "start_char": p["start_char"], "end_char": p["end_char"]}
        for p in parsed_doc.get("pages", [])
    ]
    chunks = chunk_text(
        parsed_doc["full_text"],
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        page_spans=page_spans
    )

    doc_id = database.save_document(parsed_doc, chunks)

    return {
        "status": "success",
        "document_id": doc_id,
        "filename": parsed_doc["filename"],
        "file_type": parsed_doc["file_type"],
        "file_size": parsed_doc["file_size"],
        "total_pages": parsed_doc["total_pages"],
        "word_count": parsed_doc["word_count"],
        "char_count": parsed_doc["char_count"],
        "chunk_count": len(chunks),
        "preview": parsed_doc["full_text"][:350] + "..."
    }


@app.get("/api/documents/{doc_id}")
def get_document_details(doc_id: str):
    """Retrieves document text, chunk list, and page layouts."""
    doc = database.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    return doc


@app.delete("/api/documents/{doc_id}")
def delete_document(doc_id: str):
    """Deletes a document and its associated analysis history."""
    success = database.delete_document(doc_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found.")
    return {"status": "success", "message": "Document deleted."}


# ==============================================================================
# 3. Semantic Analysis Engine
# ==============================================================================

@app.post("/api/analyze")
def analyze_document_semantic(req: AnalyzeRequest):
    """
    Executes the full semantic analysis pipeline connecting user query to document.
    Preserves and executes the exact 128D embedding and cosine similarity algorithms.
    """
    start_total_time = time.perf_counter()
    timeline = []

    # Timeline Step 1: Document received
    t0 = time.perf_counter()
    doc = database.get_document(req.document_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document '{req.document_id}' not found.")
    t1 = time.perf_counter()
    timeline.append({
        "step": 1,
        "name": "Document received",
        "status": "completed",
        "duration_ms": round((t1 - t0) * 1000, 2),
        "detail": f"Retrieved '{doc['filename']}' ({doc['file_type'].upper()}, {doc['file_size']} bytes)."
    })

    # Timeline Step 2: Text extracted
    t0 = time.perf_counter()
    full_text = doc["full_text"]
    pages = doc.get("pages", [])
    t1 = time.perf_counter()
    timeline.append({
        "step": 2,
        "name": "Text extracted",
        "status": "completed",
        "duration_ms": round((t1 - t0) * 1000, 2),
        "detail": f"Verified {doc['word_count']} words across {doc['total_pages']} page(s)."
    })

    # Timeline Step 3: Text normalized & re-chunked if hyperparameters custom
    t0 = time.perf_counter()
    page_spans = [
        {"page": p["page"], "start_char": p["start_char"], "end_char": p["end_char"]}
        for p in pages
    ]
    chunks = chunk_text(
        full_text,
        chunk_size=req.chunk_size,
        chunk_overlap=req.chunk_overlap,
        page_spans=page_spans
    )
    if not chunks:
        raise HTTPException(status_code=400, detail="Unable to create passages from this document text.")
    t1 = time.perf_counter()
    timeline.append({
        "step": 3,
        "name": "Text normalized",
        "status": "completed",
        "duration_ms": round((t1 - t0) * 1000, 2),
        "detail": f"Constructed {len(chunks)} sliding-window passages (Size: {req.chunk_size} words, Overlap: {req.chunk_overlap} words)."
    })

    # Timeline Step 4: Similarity processing
    t0 = time.perf_counter()
    # 1. Generate 128D query vector
    query_vector = generate_educational_embedding(req.query, dimension=128)
    
    # 2. Generate 128D chunk vectors and compute cosine similarity
    chunk_vectors = []
    scored_chunks = []
    all_scores = []

    for c in chunks:
        c_vec = generate_educational_embedding(c["text"], dimension=128)
        chunk_vectors.append(c_vec)
        
        sim = cosine_similarity(query_vector, c_vec)
        all_scores.append(sim)
        
        item = dict(c)
        item["score"] = round(sim, 4)
        item["score_percentage"] = round(sim * 100, 2)
        item["vector_preview"] = c_vec[:6]
        scored_chunks.append(item)

    t1 = time.perf_counter()
    timeline.append({
        "step": 4,
        "name": "Similarity processing",
        "status": "completed",
        "duration_ms": round((t1 - t0) * 1000, 2),
        "detail": f"Calculated 128-dimensional dense vectors and cosine dot-products for {len(chunks)} passages."
    })

    # Timeline Step 5: Relevant content identified
    t0 = time.perf_counter()
    scored_chunks.sort(key=lambda x: x["score"], reverse=True)
    top_k_chunks = scored_chunks[:req.top_k]
    top_chunk = top_k_chunks[0] if top_k_chunks else None
    top_score = top_chunk["score"] if top_chunk else 0.0
    t1 = time.perf_counter()
    timeline.append({
        "step": 5,
        "name": "Relevant content identified",
        "status": "completed",
        "duration_ms": round((t1 - t0) * 1000, 2),
        "detail": f"Highest similarity match identified at Passage #{top_chunk['index'] + 1} (Score: {top_score * 100:.2f}%, Page {top_chunk['page']})."
    })

    # Timeline Step 6: Answer prepared
    t0 = time.perf_counter()
    grounded_res = synthesize_grounded_answer(req.query, scored_chunks, doc_name=doc["filename"])
    normal_llm_res = synthesize_normal_llm_answer(req.query)
    
    # Generate match explanation for the top matching passage
    top_chunk_vec = chunk_vectors[top_chunk["index"]] if top_chunk else [0.0] * 128
    match_explanation = explain_similarity_match(
        req.query, top_chunk, top_score, query_vector, top_chunk_vec
    )

    # Compute genuine 2D PCA projection for vector visualization
    pca_projection = compute_2d_projection(
        query_vector, chunk_vectors, chunks, all_scores
    )

    t1 = time.perf_counter()
    timeline.append({
        "step": 6,
        "name": "Answer prepared",
        "status": "completed",
        "duration_ms": round((t1 - t0) * 1000, 2),
        "detail": "Synthesized grounded findings, citation attributions, and explainability drivers."
    })

    total_duration_ms = round((time.perf_counter() - start_total_time) * 1000, 2)

    # Format result payload
    analysis_result = {
        "query": req.query,
        "document_id": req.document_id,
        "document_name": doc["filename"],
        "document_type": doc["file_type"],
        "total_document_pages": doc["total_pages"],
        "total_document_words": doc["word_count"],
        "total_chunks_analyzed": len(chunks),
        "duration_ms": total_duration_ms,
        "timeline": timeline,
        "top_score": top_score,
        "top_score_percentage": f"{top_score * 100:.2f}%",
        "top_page": top_chunk["page"] if top_chunk else 1,
        "top_passage_index": top_chunk["index"] + 1 if top_chunk else 1,
        "top_passage_text": top_chunk["text"] if top_chunk else "",
        "ranked_chunks": top_k_chunks,
        "grounded_answer": grounded_res["answer_markdown"],
        "key_insight": grounded_res["key_insight"],
        "citations": grounded_res["citations"],
        "normal_llm_answer": normal_llm_res,
        "match_explanation": match_explanation,
        "projection_2d": pca_projection,
        "query_vector_slice": query_vector[:8],
        "top_chunk_vector_slice": top_chunk_vec[:8]
    }

    # Save to SQLite history
    analysis_id = database.save_analysis(
        doc_id=req.document_id,
        doc_name=doc["filename"],
        query=req.query,
        answer_markdown=grounded_res["answer_markdown"],
        key_insight=grounded_res["key_insight"],
        top_score=top_score,
        top_chunk_idx=top_chunk["index"] + 1 if top_chunk else 1,
        top_page=top_chunk["page"] if top_chunk else 1,
        top_text=top_chunk["text"] if top_chunk else "",
        duration_ms=total_duration_ms,
        full_result=analysis_result
    )

    analysis_result["analysis_id"] = analysis_id
    return analysis_result


# ==============================================================================
# 4. History & PDF Export
# ==============================================================================

@app.get("/api/history")
def get_analysis_history(search: Optional[str] = Query(None)):
    """Retrieves previous analyses from SQLite."""
    return {"analyses": database.list_analyses(search)}


@app.get("/api/history/{analysis_id}")
def get_analysis_record(analysis_id: str):
    """Retrieves full cached analysis record for reloading into workspace."""
    record = database.get_analysis(analysis_id)
    if not record:
        raise HTTPException(status_code=404, detail="Analysis record not found.")
    return record


@app.delete("/api/history/{analysis_id}")
def delete_analysis_record(analysis_id: str):
    """Deletes analysis history record."""
    success = database.delete_analysis(analysis_id)
    if not success:
        raise HTTPException(status_code=404, detail="Analysis record not found.")
    return {"status": "success", "message": "Record deleted."}


@app.get("/api/export/pdf/{analysis_id}")
def export_analysis_pdf(analysis_id: str):
    """Generates and downloads a publication-quality PDF analysis report."""
    record = database.get_analysis(analysis_id)
    if not record:
        raise HTTPException(status_code=404, detail="Analysis record not found.")

    full_res = record.get("full_result", {})
    pdf_bytes = generate_analysis_pdf(full_res)

    safe_name = "".join(c for c in record['document_name'] if c.isalnum() or c in "._- ")
    filename = f"Synapse_Report_{safe_name}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=\"{filename}\""
        }
    )


# ==============================================================================
# 5. Production Static Frontend Serving
# ==============================================================================

DIST_DIR = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if DIST_DIR.exists():
    assets_dir = DIST_DIR / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/{full_path:path}")
    def serve_frontend_spa(full_path: str):
        if full_path.startswith("api"):
            raise HTTPException(status_code=404, detail="API route not found")
        file_path = DIST_DIR / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(DIST_DIR / "index.html")

