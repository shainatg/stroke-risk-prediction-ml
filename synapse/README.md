# SYNAPSE // Intelligent Semantic Analysis Studio
**Production-Grade Semantic Vector Similarity & Grounded Retrieval Engine**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-v0.138%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![React 19](https://img.shields.io/badge/React-v19.0-61dafb.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-v5.8-3178c6.svg)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-v3.4-38bdf8.svg)](https://tailwindcss.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

---

## 🌟 Executive Summary

**Synapse** is an AI research web studio designed for semantic analysis, document intelligence, and grounded factual retrieval. Combining the structural refinement of Linear, the workspace versatility of Notion, and the mathematical precision of modern AI laboratories, Synapse enables researchers to ingest documents across multiple formats (**PDF, DOCX, TXT, CSV**), run fine-grained similarity queries, and inspect exactly why specific passages matched with complete algorithmic transparency.

The platform preserves and operationalizes the **128-Dimensional Semantic Vector Embedding** and **Cosine Metric** engine from first principles—guaranteeing zero fabricated numbers, zero synthetic embeddings, and verifiable source citations.

---

## 📐 Core Algorithmic Architecture

### 1. Deterministic 128-Dimensional Semantic Vector Engine
Each textual query and document passage is mapped into a continuous 128-dimensional Hilbert space:
- **TF-IDF Salience Weighting:** Common grammatical stop words are down-weighted ($w = 0.2$), while domain-specific terms are weighted dynamically proportional to character length ($w = 1.0 + \min(\text{len}/5, 1.5)$).
- **Dual Hash Mixing:** Disperses tokens across dimensions using 32-bit FNV-1a (offset `2166136261`, prime `16777619`) and DJB2 (offset `5381`) bit-shifting.
- **Linear Congruential Projection:** Deterministically pseudo-randomizes dimension contributions without requiring heavy external embedding models.
- **Subword Character 3-Grams:** Generates character tri-grams to provide morphological resilience against spelling variations and inflections.
- **L2 Unit Normalization:** Scales each vector such that $\|\mathbf{v}\|_2 = \sqrt{\sum_{i=1}^{128} v_i^2} = 1.0$.

### 2. Geometric Cosine Similarity
Because all embedding vectors are unit normalized onto a 128D hypersphere, the cosine similarity simplifies to the geometric inner dot product:
$$\cos(\theta) = \frac{\mathbf{q} \cdot \mathbf{c}}{\|\mathbf{q}\|_2 \|\mathbf{c}\|_2} = \sum_{d=1}^{128} q_d \cdot c_d$$

### 3. Sliding Window Passage Chunking with Overlap
Prevents boundary splitting dilemmas where critical facts spanning sentence thresholds are severed:
$$\text{Stride } S = C - O, \quad \text{Total Chunks} = \left\lceil \frac{N - O}{S} \right\rceil$$
Where $C$ is the chunk size in words and $O$ is the boundary overlap (default: $C=25, O=6$).

### 4. 2D PCA Dimensionality Reduction
To visualize the 128D vector space in the **Semantic Similarity Lab**, Synapse fits Principal Component Analysis (`sklearn.decomposition.PCA`) on the exact matrix containing the query vector and chunk vectors, projecting them into authentic 2D Cartesian coordinates with verified explained variance ratios.

---

## 🖥️ Application Experience & Three-Panel Layout

### 1. Knowledge Sources (Left Panel)
- **Drag-and-Drop Ingestion:** Accepts PDF, DOCX, TXT, and CSV files (up to 25MB).
- **Metadata Cards:** Displays document format badges, file size, word counts, passage counts, and page numbers.
- **Corpora Management:** Search through loaded files, remove/replace active files, and switch active documents.
- **Pre-loaded Research Corpora:** Includes pre-packaged research whitepapers:
  - *Quantum Information Science & Cryogenics (PDF/TXT)*
  - *Corporate Remote Work & Travel Security Policy SEC-2026-v4 (DOCX)*
  - *NASA Mars Perseverance Rover & MOXIE Mission Report (TXT)*
  - *Clinical Patient Diagnoses Cohort (CSV)*

### 2. Semantic Query Studio (Center Panel)
- **Editorial Query Textarea:** High-contrast, clean editor with word and character counters.
- **Keyboard Accelerators:** Press `Ctrl + Enter` (or `Cmd + Enter`) to instantly launch analysis.
- **Dynamic Contextual Prompts:** Recommends targeted research questions tailored to the active document.
- **Hyperparameter Controls:** Interactive sliders to adjust Chunk Size (words), Chunk Overlap (words), and Top-K retrieved passages.
- **Live Execution Timeline:** Displays actual backend milestone timings:
  1. *Document received*
  2. *Text extracted*
  3. *Text normalized*
  4. *Similarity processing*
  5. *Relevant content identified*
  6. *Answer prepared*

### 3. Intelligence Results (Right Panel)
- **Grounded Finding:** Formatted Markdown answer with verified passage quotes and primary insights.
- **Peak Similarity Metric:** High-visibility badge indicating the highest cosine score percentage.
- **Verified Citations:** Page references and passage indices (e.g., *Passage #2, Page 1 • 35.9% Match*).
- **Explainable Match Drivers:** Reveals exact co-occurring vocabulary, morphological stem matches, and inner dot-product contributions.
- **Pure LLM Simulator Contrast:** Side-by-side comparison illustrating why ungrounded language models fail on proprietary/private documents without RAG.
- **Export & Action Suite:** One-click copy, publication-grade PDF report download, and direct inspection in the Document Viewer.

---

## 🔬 Specialized Workspaces & Modals

- **Semantic Similarity Lab:** Dedicated interactive laboratory featuring horizontal Recharts similarity leaderboards, authentic 2D PCA vector space scatter plots, and algorithmic mathematical audits.
- **Document Inspection Viewer:** Page-by-page reader with zoom controls (80%–160%), full-text search, and automated passage highlighting jumping to citation coordinates.
- **Pipeline Explorer:** Interactive 7-phase architecture blueprint explaining the exact data transformations from raw byte streams to synthesized findings.
- **Research History Drawer:** Searchable SQLite-backed history storing prior queries, scores, and findings with one-click reload.

---

## 🚀 Quickstart & Execution Instructions

### 1. Prerequisites
- Python 3.10, 3.11, 3.12, or 3.13.
- Node.js 18+ (Node 24 tested) and npm.

### 2. Launching the Unified Studio (Recommended)

Run the unified production runner from the project root:

```bash
cd "c:\Users\shaina\OneDrive\Desktop\mini project"
python synapse/run.py
```

Open your browser and navigate to:
👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

*The FastAPI service automatically serves both the complete REST API and the pre-built, production-minified React SPA!*

### 3. Development Mode (Optional)

If you wish to run the frontend with Vite Hot Module Replacement (HMR):

**Terminal 1 (Backend API):**
```bash
python synapse/run.py
# Backend runs on http://127.0.0.1:8000
```

**Terminal 2 (Frontend Dev Server):**
```bash
cd synapse/frontend
npm run dev
# Frontend runs on http://localhost:5173 and proxies /api to 8000
```

---

## 🧪 Automated Verification & Testing

Synapse includes a comprehensive automated test suite verifying vector determinism, unit normalization, chunk boundary preservation, multi-format parsing, 2D PCA, PDF generation, and all FastAPI endpoints:

```bash
python synapse/backend/tests/test_engine.py
```

---

## 📡 REST API Reference

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `GET /api/health` | `GET` | Health check, runtime version, and 128D embedding confirmation |
| `GET /api/pipeline/info` | `GET` | Technical specifications of all 7 pipeline phases |
| `GET /api/documents` | `GET` | Lists uploaded documents and sample corpora |
| `POST /api/documents/upload` | `POST` | Multipart upload for PDF, DOCX, TXT, and CSV files |
| `POST /api/documents/load-sample` | `POST` | Loads a pre-packaged sample document into SQLite |
| `GET /api/documents/{id}` | `GET` | Retrieves full document text, page maps, and chunk data |
| `DELETE /api/documents/{id}` | `DELETE` | Deletes a document and its analysis records |
| `POST /api/analyze` | `POST` | Executes similarity algorithm, returns scores, grounded answer, timeline, and PCA |
| `GET /api/history` | `GET` | Retrieves saved analyses with optional search query |
| `GET /api/history/{id}` | `GET` | Fetches a specific analysis record |
| `DELETE /api/history/{id}` | `DELETE` | Deletes an analysis record |
| `GET /api/export/pdf/{id}` | `GET` | Streams a publication-grade PDF analysis report |

---

## ⚖️ Academic & Research Integrity Guarantee

- **No Fabricated Scores:** Every similarity metric is computed using real cosine math over 128D vectors.
- **No Synthetic Embeddings:** The 2D PCA projection uses real scikit-learn SVD components derived from actual passage vectors.
- **No Hallucinated Citations:** Quotations in grounded answers are extracted verbatim from the uploaded document text.
