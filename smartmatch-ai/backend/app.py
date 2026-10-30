"""
SmartMatch AI - Flask Backend Server
=====================================
A clean, modern, beginner-friendly Flask application providing an endpoint
for analyzing text similarity between user questions and uploaded documents.

Endpoints:
- POST /api/analyze         : Core endpoint to analyze text against PDF, DOCX, or TXT
- GET  /api/samples         : List preloaded educational sample files
- GET  /api/samples/<name>  : Retrieve content of a sample file
- GET  /api/health          : Service health check & active ML engine info
- GET  /                    : Serves the React frontend (when built)

Technology Stack:
- Python 3.10+
- Flask & Flask-CORS
- Scikit-learn (TfidfVectorizer & cosine_similarity)
- PyMuPDF (PDF parsing)
- python-docx (Word document parsing)
"""

import os
import sys
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Import our custom extraction and similarity modules
from document_extractor import extract_document_text, split_into_paragraphs
from similarity_engine import compute_tfidf_similarity, generate_professor_embedding, professor_cosine_similarity

# Configure paths
BASE_DIR = Path(__file__).resolve().parent
SAMPLE_DIR = BASE_DIR / "sample_data"
FRONTEND_DIST = BASE_DIR.parent / "frontend" / "dist"

# Initialize Flask application
app = Flask(__name__, static_folder=str(FRONTEND_DIST) if FRONTEND_DIST.exists() else None)

# Enable Cross-Origin Resource Sharing (CORS) for development with Vite
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Configuration
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB maximum file upload limit
ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}


def is_allowed_file(filename: str) -> bool:
    """Checks if the uploaded file has a supported extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ==============================================================================
# API ROUTES
# ==============================================================================

@app.route("/api/health", methods=["GET"])
def health_check():
    """
    Health check endpoint returning system status and loaded ML capabilities.
    """
    return jsonify({
        "status": "healthy",
        "service": "SmartMatch AI — Document Similarity Checker",
        "version": "1.0.0",
        "engine": "Scikit-Learn TF-IDF + Cosine Similarity",
        "supported_formats": [".pdf", ".docx", ".txt"],
        "max_upload_mb": 16,
        "sample_documents_available": len(list(SAMPLE_DIR.glob("*.*"))) if SAMPLE_DIR.exists() else 0
    })


@app.route("/api/samples", methods=["GET"])
def list_samples():
    """
    Returns the list of preloaded educational sample files for quick 1-click testing.
    """
    samples = []
    if SAMPLE_DIR.exists():
        for f in SAMPLE_DIR.iterdir():
            if f.is_file() and is_allowed_file(f.name):
                ext = f.suffix.lower().replace(".", "")
                
                # Assign user-friendly sample query suggestions
                suggested_query = "What is the main topic of this document?"
                if "diabetes" in f.name:
                    suggested_query = "What are the main causes of diabetes?"
                elif "ai" in f.name or "artificial" in f.name:
                    suggested_query = "How does TF-IDF and cosine similarity work in NLP?"
                elif "climate" in f.name:
                    suggested_query = "What are the primary drivers of global warming and climate change?"
                elif "quantum" in f.name:
                    suggested_query = "How do qubits and superposition differ from classical bits?"

                samples.append({
                    "filename": f.name,
                    "extension": ext,
                    "size_bytes": f.stat().st_size,
                    "size_formatted": f"{f.stat().st_size / 1024:.1f} KB",
                    "suggested_query": suggested_query
                })
    return jsonify({"status": "success", "samples": samples})


@app.route("/api/analyze", methods=["POST"])
def analyze_document_similarity():
    """
    Core similarity endpoint.
    Accepts:
    - Form field 'text' (the question or search text)
    - Form file 'file' (uploaded PDF, DOCX, or TXT)
      OR form field 'sample_filename' (to use a preloaded sample document)
    
    Returns:
    - JSON with question, best matching paragraph, similarity score, source document.
    """
    # 1. Validate User Query / Text
    user_query = request.form.get("text", "").strip()
    if not user_query:
        return jsonify({
            "status": "error",
            "error_code": "EMPTY_QUERY",
            "message": "Please enter a question or text in the text box before analyzing."
        }), 400

    # 2. Retrieve Uploaded File or Selected Sample File
    file_bytes = None
    filename = None

    if "file" in request.files and request.files["file"].filename != "":
        uploaded_file = request.files["file"]
        filename = secure_filename(uploaded_file.filename)
        
        if not is_allowed_file(filename):
            return jsonify({
                "status": "error",
                "error_code": "UNSUPPORTED_FORMAT",
                "message": f"Unsupported file type for '{filename}'. Please upload a PDF, DOCX, or TXT file."
            }), 400
            
        file_bytes = uploaded_file.read()
        
    elif "sample_filename" in request.form and request.form["sample_filename"].strip():
        # User selected one of the preloaded educational sample files
        sample_name = secure_filename(request.form["sample_filename"].strip())
        sample_path = SAMPLE_DIR / sample_name
        
        if not sample_path.exists():
            return jsonify({
                "status": "error",
                "error_code": "SAMPLE_NOT_FOUND",
                "message": f"Sample document '{sample_name}' was not found on the server."
            }), 404
            
        filename = sample_name
        with open(sample_path, "rb") as f:
            file_bytes = f.read()
    else:
        return jsonify({
            "status": "error",
            "error_code": "NO_FILE_UPLOADED",
            "message": "Please upload a document (.pdf, .docx, or .txt) to compare against."
        }), 400

    # 3. Extract Text from the Document
    try:
        raw_text = extract_document_text(file_bytes, filename)
    except Exception as e:
        return jsonify({
            "status": "error",
            "error_code": "EXTRACTION_FAILED",
            "message": f"Error extracting text from '{filename}': {str(e)}"
        }), 422

    if not raw_text or not raw_text.strip():
        return jsonify({
            "status": "error",
            "error_code": "EMPTY_DOCUMENT",
            "message": f"The file '{filename}' was read successfully but contains no readable text."
        }), 422

    # 4. Segment Document into Semantic Paragraphs
    paragraphs = split_into_paragraphs(raw_text)
    if not paragraphs:
        return jsonify({
            "status": "error",
            "error_code": "NO_PARAGRAPHS",
            "message": "Could not identify any substantial paragraphs in the document to compare."
        }), 422

    # 5. Compute TF-IDF Vectors & Cosine Similarity using Scikit-Learn
    similarity_result = compute_tfidf_similarity(user_query, paragraphs, top_k=3)

    best_match = similarity_result.get("best_match")
    top_score = similarity_result.get("top_score", 0.0)
    top_percentage = similarity_result.get("top_percentage", 0.0)

    # 6. Format Response
    if best_match and top_score > 0.02:
        answer_text = best_match["text"]
        match_found = True
    else:
        answer_text = (
            "No closely related information could be found in the uploaded document "
            "for your specific question. Please try rephrasing your question with keywords "
            "found inside the document."
        )
        match_found = False

    return jsonify({
        "status": "success",
        "match_found": match_found,
        "question": user_query,
        "answer": answer_text,
        "similarity_score": top_score,
        "similarity_percentage": top_percentage,
        "confidence_label": similarity_result.get("confidence_label", "Moderate"),
        "confidence_color": similarity_result.get("confidence_color", "blue"),
        "source_document": filename,
        "file_size_bytes": len(file_bytes),
        "total_paragraphs_compared": len(paragraphs),
        "best_paragraph_index": best_match["index"] if best_match else None,
        "matched_terms": best_match["matched_terms"] if best_match else [],
        "candidates": similarity_result.get("candidates", []),
        "algorithm": similarity_result.get("algorithm", "Scikit-Learn TF-IDF + Cosine"),
        "educational_note": (
            "The similarity score reflects vector alignment and vocabulary overlap "
            "between your question and the source text; it does not indicate statistical truth."
        )
    })


# ==============================================================================
# STATIC FRONTEND SERVING (SINGLE-PORT DEPLOYMENT)
# ==============================================================================

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path):
    """
    Serves the built React application from frontend/dist if available.
    """
    if FRONTEND_DIST.exists():
        target = FRONTEND_DIST / path
        if path != "" and target.exists():
            return send_from_directory(str(FRONTEND_DIST), path)
        return send_from_directory(str(FRONTEND_DIST), "index.html")
    
    return (
        "<h2>SmartMatch AI API is Running</h2>"
        "<p>Backend is active. Please start the Vite frontend using <code>npm run dev</code> "
        "or build it using <code>npm run build</code>.</p>"
    )


# ==============================================================================
# SERVER ENTRY POINT
# ==============================================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    print("=" * 70)
    print("  SMARTMATCH AI — DOCUMENT SIMILARITY CHECKER")
    print("  Flask & Scikit-Learn NLP Backend Service")
    print("=" * 70)
    print(f"  * Backend URL: http://127.0.0.1:{port}")
    print(f"  * Sample Files: {SAMPLE_DIR}")
    print("=" * 70)
    app.run(host="127.0.0.1", port=port, debug=True)
