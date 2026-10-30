"""
Synapse Production Server Entrypoint
====================================
Runs the full Synapse Semantic Analysis Studio (FastAPI backend + React frontend).
Accessible at: http://127.0.0.1:8000
"""

import sys
import uvicorn
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR / "backend"))

if __name__ == "__main__":
    print("=" * 72)
    print("  SYNAPSE // INTELLIGENT SEMANTIC ANALYSIS STUDIO")
    print("  128D Multi-Dimensional Semantic Vector Similarity Engine")
    print("=" * 72)
    print("  * Unified Web Studio URL: http://127.0.0.1:8000")
    print("  * REST API Docs (Swagger): http://127.0.0.1:8000/docs")
    print("  * Storage: SQLite Database & Local Uploads")
    print("=" * 72)
    print("  Starting Uvicorn server...\n")

    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=False)
