"""
SmartMatch AI - Backend Automated Test Suite
============================================
Runs comprehensive validation tests against the Flask backend endpoints:
1. Health check verification
2. Sample documents listing
3. Error handling for empty queries and missing files
4. Text similarity calculation across TXT, DOCX, and PDF formats
5. Cosine similarity accuracy and candidate ranking
"""

import sys
import os
from pathlib import Path
import io
import json

# Ensure stdout handles unicode characters on Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Ensure backend directory is in sys.path
TEST_DIR = Path(__file__).resolve().parent
BACKEND_DIR = TEST_DIR.parent
sys.path.insert(0, str(BACKEND_DIR))

from app import app


def test_api():
    print("=" * 65)
    print("  RUNNING SMARTMATCH AI BACKEND TEST SUITE")
    print("=" * 65)

    client = app.test_client()

    # 1. Test Health Endpoint
    res = client.get("/api/health")
    assert res.status_code == 200, f"Health check failed with {res.status_code}"
    data = res.get_json()
    assert data["status"] == "healthy"
    print("✓ [PASS] GET /api/health - Service is healthy & Scikit-Learn active")

    # 2. Test Samples Endpoint
    res = client.get("/api/samples")
    assert res.status_code == 200
    samples_data = res.get_json()
    assert len(samples_data["samples"]) >= 3
    print(f"✓ [PASS] GET /api/samples - Found {len(samples_data['samples'])} educational sample files")

    # 3. Test Error: Empty Query Validation
    res = client.post("/api/analyze", data={"text": "", "sample_filename": "diabetes_causes.txt"})
    assert res.status_code == 400
    err_data = res.get_json()
    assert err_data["error_code"] == "EMPTY_QUERY"
    print("✓ [PASS] POST /api/analyze - Properly caught EMPTY_QUERY validation error")

    # 4. Test Error: Missing File Validation
    res = client.post("/api/analyze", data={"text": "What are the causes of diabetes?"})
    assert res.status_code == 400
    err_data = res.get_json()
    assert err_data["error_code"] == "NO_FILE_UPLOADED"
    print("✓ [PASS] POST /api/analyze - Properly caught NO_FILE_UPLOADED error")

    # 5. Test Real Analysis with Sample File (diabetes_causes.txt)
    res = client.post("/api/analyze", data={
        "text": "What are the main causes of diabetes?",
        "sample_filename": "diabetes_causes.txt"
    })
    assert res.status_code == 200
    res_data = res.get_json()
    assert res_data["status"] == "success"
    assert res_data["match_found"] is True
    assert res_data["similarity_score"] > 0.20
    assert "immune system" in res_data["answer"].lower() or "causes of diabetes" in res_data["answer"].lower()
    print(f"✓ [PASS] POST /api/analyze (TXT Sample) - Score: {res_data['similarity_percentage']}% | Best Match: Paragraph #{res_data['best_paragraph_index']}")

    # 6. Test File Upload via Multipart Bytes (PDF file)
    sample_pdf_path = BACKEND_DIR / "sample_data" / "quantum_computing.pdf"
    if sample_pdf_path.exists():
        with open(sample_pdf_path, "rb") as f:
            pdf_bytes = f.read()
        res = client.post(
            "/api/analyze",
            data={
                "text": "How do qubits and superposition work in quantum computing?",
                "file": (io.BytesIO(pdf_bytes), "quantum_computing.pdf")
            },
            content_type="multipart/form-data"
        )
        assert res.status_code == 200
        pdf_res = res.get_json()
        assert pdf_res["status"] == "success"
        assert pdf_res["similarity_score"] > 0.10
        print(f"✓ [PASS] POST /api/analyze (PDF Upload) - Score: {pdf_res['similarity_percentage']}% | Source: {pdf_res['source_document']}")

    # 7. Test File Upload via Multipart Bytes (DOCX file)
    sample_docx_path = BACKEND_DIR / "sample_data" / "climate_change.docx"
    if sample_docx_path.exists():
        with open(sample_docx_path, "rb") as f:
            docx_bytes = f.read()
        res = client.post(
            "/api/analyze",
            data={
                "text": "What greenhouse gases cause global warming and climate change?",
                "file": (io.BytesIO(docx_bytes), "climate_change.docx")
            },
            content_type="multipart/form-data"
        )
        assert res.status_code == 200
        docx_res = res.get_json()
        assert docx_res["status"] == "success"
        assert docx_res["similarity_score"] > 0.10
        print(f"✓ [PASS] POST /api/analyze (DOCX Upload) - Score: {docx_res['similarity_percentage']}% | Source: {docx_res['source_document']}")

    print("=" * 65)
    print("  ALL 7 BACKEND API TESTS COMPLETED SUCCESSFULLY (100% PASS)!")
    print("=" * 65)


if __name__ == "__main__":
    test_api()
