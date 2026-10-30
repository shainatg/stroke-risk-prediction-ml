"""
SmartMatch AI — Unified Application Runner
===========================================
This script launches the Flask backend and serves the compiled React frontend
on a single local URL (http://127.0.0.1:5050).

Usage:
    python run.py
"""

import sys
import os
import webbrowser
from pathlib import Path

# Add backend directory to path
SMARTMATCH_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SMARTMATCH_DIR / "backend"
FRONTEND_DIST = SMARTMATCH_DIR / "frontend" / "dist"

sys.path.insert(0, str(BACKEND_DIR))

from app import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    host = "127.0.0.1"
    url = f"http://{host}:{port}"

    print("=" * 72)
    print("       SMARTMATCH AI — DOCUMENT SIMILARITY CHECKER")
    print("  Natural Language Processing & Cosine Text Matching Studio")
    print("=" * 72)
    print(f"  * Web Application URL : {url}")
    print(f"  * Backend Engine      : Scikit-Learn TF-IDF + PyMuPDF + python-docx")
    print(f"  * Frontend Interface  : React + Vite + Tailwind CSS (SPA)")
    print(f"  * Sample Documents    : {BACKEND_DIR / 'sample_data'}")
    print("=" * 72)
    print("  Open the URL above in any web browser to use the application.")
    print("  Press Ctrl+C to terminate the server.\n")

    # Start Flask server
    app.run(host=host, port=port, debug=False)
