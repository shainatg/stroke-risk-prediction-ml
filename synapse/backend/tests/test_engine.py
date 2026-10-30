"""
Synapse Comprehensive Engine & API Test Suite
=============================================
Verifies 128D mathematical vector embeddings, cosine ranking, chunking with overlap,
multi-format document parsing (PDF, DOCX, TXT, CSV), 2D PCA projection,
PDF report generation, and FastAPI endpoints.
"""

import sys
import os
import math
import io
from pathlib import Path

# Force UTF-8 stdout on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add backend directory to path
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from core.similarity_engine import (
    generate_educational_embedding,
    cosine_similarity,
    chunk_text
)
from core.document_parser import DocumentParser
from core.synthesizer import synthesize_grounded_answer, explain_similarity_match
from core.projection import compute_2d_projection
from core.report_generator import generate_analysis_pdf
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_all():
    print("=" * 70)
    print("🧪 Running Comprehensive Backend & Algorithm Tests for Synapse")
    print("=" * 70)

    # 1. 128D Embedding Tests
    query = "What cryogenic temperatures are used in quantum computing dilution refrigerators?"
    vec = generate_educational_embedding(query, 128)
    assert len(vec) == 128, f"Expected 128 dimensions, got {len(vec)}"
    print("✅ 128-dimensional dense vector generated successfully.")

    vec2 = generate_educational_embedding(query, 128)
    assert vec == vec2, "Embedding must be 100% deterministic."
    print("✅ Embedding determinism verified.")

    norm = math.sqrt(sum(x * x for x in vec))
    assert abs(norm - 1.0) < 0.001, f"Expected unit norm 1.0, got {norm}"
    print(f"✅ L2 Unit Normalization verified: ||v|| = {norm:.4f}")

    # 2. Cosine Similarity Ranking Tests
    relevant = "Quantum processors are housed in cryogenic dilution refrigerators cooled to 15 millikelvin near absolute zero."
    irrelevant = "Bake the chocolate chip cookies for 12 minutes until edges are golden brown."

    vec_rel = generate_educational_embedding(relevant, 128)
    vec_irrel = generate_educational_embedding(irrelevant, 128)

    sim_self = cosine_similarity(vec, vec)
    assert abs(sim_self - 1.0) < 0.001, f"Self similarity must be 1.0, got {sim_self}"

    sim_rel = cosine_similarity(vec, vec_rel)
    sim_irrel = cosine_similarity(vec, vec_irrel)
    print(f"   Self similarity: {sim_self:.4f}")
    print(f"   Relevant chunk match: {sim_rel:.4f} ({sim_rel * 100:.1f}%)")
    print(f"   Distractor chunk match: {sim_irrel:.4f} ({sim_irrel * 100:.1f}%)")
    assert sim_rel > sim_irrel, "Relevant text must rank higher than distractor."
    print("✅ Semantic cosine similarity discrimination verified.")

    # 3. Chunking & Overlap Tests
    sample_text = "one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty"
    chunks = chunk_text(sample_text, chunk_size=8, chunk_overlap=3)
    assert len(chunks) >= 3, "Sliding window chunker failed to produce chunks."
    assert chunks[0]["overlapNext"] == " ".join(chunks[1]["text"].split()[:3])
    print(f"✅ Sliding window chunker verified ({len(chunks)} chunks, overlap preserved).")

    # 4. Multi-format Document Parsing
    sample_dir = BACKEND_DIR / "sample_data"
    
    # Test TXT
    txt_doc = DocumentParser.parse_file(sample_dir / "quantum_computing_cryogenics.txt", "quantum.txt")
    assert txt_doc["word_count"] > 100
    print(f"✅ TXT parsing verified ({txt_doc['word_count']} words).")

    # Test CSV
    csv_doc = DocumentParser.parse_file(sample_dir / "clinical_stroke_cohort.csv", "stroke.csv")
    assert csv_doc["word_count"] > 30
    print(f"✅ CSV parsing verified ({csv_doc['word_count']} words, structured rows).")

    # Test DOCX
    docx_doc = DocumentParser.parse_file(sample_dir / "corporate_travel_policy_sec2026.docx", "policy.docx")
    assert docx_doc["word_count"] > 50
    print(f"✅ DOCX parsing verified ({docx_doc['word_count']} words).")

    # Test PDF
    pdf_doc = DocumentParser.parse_file(sample_dir / "quantum_computing_whitepaper.pdf", "whitepaper.pdf")
    assert pdf_doc["total_pages"] >= 1
    assert pdf_doc["word_count"] > 50
    print(f"✅ PDF parsing verified ({pdf_doc['word_count']} words, page-tracked).")

    # 5. 2D PCA Projection
    chunk_vecs = [generate_educational_embedding(c["text"], 128) for c in chunks[:5]]
    scores = [cosine_similarity(vec, cv) for cv in chunk_vecs]
    proj = compute_2d_projection(vec, chunk_vecs, chunks[:5], scores)
    assert proj["available"] is True
    assert len(proj["points"]) == 1 + len(chunk_vecs)
    print(f"✅ 2D PCA projection verified (Variance explained: {proj['variance_explained']}).")

    # 6. PDF Report Generation
    test_analysis_data = {
        "document_name": "Test Document.pdf",
        "query": query,
        "top_score": sim_rel,
        "duration_ms": 14.2,
        "top_page": 1,
        "key_insight": "Quantum processors are cooled to 15 millikelvin.",
        "top_passage_text": relevant,
        "ranked_chunks": [{"index": 0, "page": 1, "score": sim_rel, "text": relevant}],
        "match_explanation": explain_similarity_match(query, {"text": relevant}, sim_rel, vec, vec_rel)
    }
    pdf_bytes = generate_analysis_pdf(test_analysis_data)
    assert pdf_bytes.startswith(b"%PDF"), "Report generator did not produce valid PDF bytes."
    print(f"✅ Publication-grade PDF report generated ({len(pdf_bytes)} bytes).")

    # 7. FastAPI Endpoint Tests
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "online"
    print("✅ FastAPI /api/health verified.")

    res = client.get("/api/pipeline/info")
    assert res.status_code == 200
    assert len(res.json()["stages"]) == 7
    print("✅ FastAPI /api/pipeline/info verified (7 pipeline stages).")

    # Load a sample document via API
    res = client.post("/api/documents/load-sample?sample_name=quantum_computing_whitepaper.pdf")
    assert res.status_code == 200
    doc_id = res.json()["document_id"]
    print(f"✅ FastAPI document load verified (Doc ID: {doc_id}).")

    # Analyze document via API
    res = client.post("/api/analyze", json={
        "document_id": doc_id,
        "query": "How cold is the dilution refrigerator?",
        "chunk_size": 25,
        "chunk_overlap": 6,
        "top_k": 3
    })
    assert res.status_code == 200
    analysis = res.json()
    assert analysis["top_score"] > 0.15
    assert len(analysis["ranked_chunks"]) <= 3
    assert len(analysis["timeline"]) == 6
    assert "refrigerator" in analysis["top_passage_text"].lower() or "millikelvin" in analysis["top_passage_text"].lower()
    print(f"✅ FastAPI /api/analyze verified (Top Score: {analysis['top_score_percentage']}, Latency: {analysis['duration_ms']}ms).")

    print("\n" + "=" * 70)
    print("🎉 ALL BACKEND ALGORITHM & API TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 70)

if __name__ == "__main__":
    test_all()
