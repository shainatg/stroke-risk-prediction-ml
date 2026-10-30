# SmartMatch AI — Document Similarity Checker

> **"Upload a document, ask a question, and find the most relevant answer."**

A modern, beginner-friendly, and interactive single-page web application designed for university presentations and practical demonstrations of **Natural Language Processing (NLP)**, **TF-IDF Vectorization**, and **Cosine Text Similarity**.

---

## 🌟 Key Features

1. **Multi-Format Document Extraction**:
   - **PDF (`.pdf`)**: Parsed page-by-page using high-performance **PyMuPDF** (`fitz`).
   - **Word (`.docx`)**: Parsed paragraph-by-paragraph using **python-docx**.
   - **Plain Text (`.txt`)**: Decoded using UTF-8 and Latin-1 fallback encoders.
2. **Scikit-Learn NLP Engine**:
   - Computes **Term Frequency-Inverse Document Frequency (TF-IDF)** matrices using `sklearn.feature_extraction.text.TfidfVectorizer`.
   - Evaluates multi-dimensional **Cosine Similarity** using `sklearn.metrics.pairwise.cosine_similarity`.
3. **White & Light-Blue Modern Interface**:
   - Built with **React 19**, **Vite**, **Tailwind CSS**, and **Lucide React**.
   - Rounded cards, clean spacing, interactive buttons, character counters, and progress bars.
   - Drag-and-drop file upload with animated states.
   - Preloaded 1-click educational sample documents (`.pdf`, `.docx`, `.txt`) for instant testing.
4. **Explainability & Grounding**:
   - Highlights the exact matching paragraph directly from the source file.
   - Displays real calculated similarity percentage and vector cosine score.
   - Shows matched vocabulary tokens and relative ranking against other candidate paragraphs.
   - One-click clipboard copy and reset actions.

---

## 🏗️ Technology Stack

| Layer | Technologies Used | Purpose |
| :--- | :--- | :--- |
| **Frontend** | React 19, Vite, Tailwind CSS 3.4 | Modern, fast, responsive single-page web application |
| **Icons** | Lucide React | Clean, intuitive icons for drag-and-drop, files, and status |
| **Backend** | Python 3.10+, Flask, Flask-CORS | REST API handling file uploads, text parsing, and similarity |
| **NLP & ML** | Scikit-learn (`sklearn`) | TF-IDF numerical vectorization and cosine similarity calculation |
| **PDF Parser** | PyMuPDF (`fitz`) | Robust extraction of text streams from PDF files |
| **DOCX Parser** | `python-docx` | Extraction of text and tables from Microsoft Word files |

---

## 📁 Project Directory Structure

```text
smartmatch-ai/
├── run.py                          # Unified launcher (starts backend & serves built React SPA)
├── README.md                       # Comprehensive guide and college viva notes
├── backend/
│   ├── app.py                      # Flask REST API server with /api/analyze endpoint
│   ├── document_extractor.py       # Extraction logic for PDF, Word (.docx), and Text (.txt)
│   ├── similarity_engine.py        # TF-IDF Vectorizer + Cosine Similarity scoring
│   ├── requirements.txt            # Python dependencies
│   ├── generate_samples.py         # Script to generate sample test files
│   ├── sample_data/                # Built-in educational sample documents
│   │   ├── diabetes_causes.txt     # Medical overview matching requested placeholder
│   │   ├── artificial_intelligence.txt # AI & NLP fundamentals
│   │   ├── climate_change.docx     # Microsoft Word document on global warming
│   │   └── quantum_computing.pdf   # Formatted PDF on qubits and superposition
│   └── tests/
│       └── test_api.py             # 7 automated tests for backend validation
└── frontend/
    ├── index.html                  # HTML entry point with Inter font & favicon
    ├── package.json                # React, Vite, and Tailwind dependencies
    ├── vite.config.js              # Vite configuration with proxy to Flask
    ├── tailwind.config.js          # White & light-blue theme color palette
    ├── postcss.config.js           # PostCSS setup for Tailwind
    └── src/
        ├── main.jsx                # React DOM render entry
        ├── App.jsx                 # Main stateful application component
        ├── index.css               # Custom CSS styles, glass cards, and scrollbars
        └── components/
            ├── Header.jsx          # Title, subtitle, and badges
            ├── TextInput.jsx       # Question input, character counter, sample chips
            ├── FileUpload.jsx      # Drag-and-drop upload zone & sample selector
            ├── ActionButton.jsx    # "Find Similarity & Generate Answer" button
            ├── ResultsCard.jsx     # Result card, progress bar, copy button
            ├── WorkflowSection.jsx # 4-step workflow cards at bottom
            └── HowItWorksModal.jsx # Educational math popup for presentations
```

---

## 🧠 How Similarity Works (College Presentation Guide)

When presenting this project to your professor, you can explain the 4 stages of the pipeline:

### 1. Document Extraction & Segmentation
The uploaded document is read as binary bytes. Based on its file extension:
- **PDF**: PyMuPDF extracts text streams across all pages.
- **DOCX**: python-docx extracts paragraphs and tables.
- **TXT**: Decoded with UTF-8 / Latin-1 detection.
The document text is then split into individual logical paragraphs ($P_1, P_2, \dots, P_n$).

### 2. TF-IDF Numerical Vectorization
Computers cannot compare text strings directly. We convert both the user's question $Q$ and each document paragraph $P_i$ into multi-dimensional vectors using **TF-IDF**:

$$\text{TF-IDF}(t, d, D) = \text{TF}(t, d) \times \log\left(\frac{N}{\text{DF}(t)}\right)$$

- **Term Frequency (TF)**: How frequently term $t$ appears in paragraph $d$.
- **Inverse Document Frequency (IDF)**: Penalizes common grammatical words (*"the"*, *"is"*) and awards higher mathematical weights to domain-specific keywords (*"diabetes"*, *"insulin"*, *"causes"*).

### 3. Cosine Similarity Metric
We measure the cosine of the angle $\theta$ between the query vector $\mathbf{A}$ and paragraph vector $\mathbf{B}$:

$$\text{Cosine Similarity} = \cos(\theta) = \frac{\mathbf{A} \cdot \mathbf{B}}{\|\mathbf{A}\|_2 \times \|\mathbf{B}\|_2} = \frac{\sum_{i=1}^{n} A_i B_i}{\sqrt{\sum_{i=1}^{n} A_i^2} \sqrt{\sum_{i=1}^{n} B_i^2}}$$

- **1.0 (100%)**: Vectors point in identical orientation (maximum vocabulary overlap).
- **0.0 (0%)**: Vectors are orthogonal (no shared semantic terms).

### 4. Ranked Answer Retrieval
The system ranks all paragraphs by similarity score descending, identifies the paragraph with the highest cosine score, and returns it as the **Most Relevant Answer**.

> ℹ️ **Important Educational Note:** The similarity score measures *textual and semantic alignment*, not the scientific probability that the source answer is factually true.

---

## 🚀 How to Run the Project

### Option A: 1-Command Unified Run (Recommended)
This runs the Flask backend and serves the compiled React frontend together on a single port:

```bash
# 1. From the project root, launch the application
python smartmatch-ai/run.py
```

Open your browser to:
👉 **`http://127.0.0.1:5050`**

---

### Option B: Development Mode (Hot-Reloading)
If you want to edit the React frontend and see changes update live:

```bash
# Terminal 1: Start the Flask Backend
cd smartmatch-ai/backend
python app.py

# Terminal 2: Start the Vite Dev Server
cd smartmatch-ai/frontend
npm run dev
```

Open your browser to:
👉 **`http://localhost:5173`** (Vite automatically proxies API requests to Flask on port 5050).

---

## 🧪 Testing the Application

### Automated Test Suite
You can verify all endpoints and similarity algorithms automatically:

```bash
python smartmatch-ai/backend/tests/test_api.py
```

**Output:**
```text
=================================================================
  RUNNING SMARTMATCH AI BACKEND TEST SUITE
=================================================================
✓ [PASS] GET /api/health - Service is healthy & Scikit-Learn active
✓ [PASS] GET /api/samples - Found 4 educational sample files
✓ [PASS] POST /api/analyze - Properly caught EMPTY_QUERY validation error
✓ [PASS] POST /api/analyze - Properly caught NO_FILE_UPLOADED error
✓ [PASS] POST /api/analyze (TXT Sample) - Score: 27.1% | Best Match: Paragraph #3
✓ [PASS] POST /api/analyze (PDF Upload) - Score: 12.2% | Source: quantum_computing.pdf
✓ [PASS] POST /api/analyze (DOCX Upload) - Score: 18.9% | Source: climate_change.docx
=================================================================
  ALL 7 BACKEND API TESTS COMPLETED SUCCESSFULLY (100% PASS)!
=================================================================
```

---

## 📋 REST API Endpoints

### 1. `GET /api/health`
Checks backend status and verifies NLP dependencies.
- **Response**:
```json
{
  "status": "healthy",
  "service": "SmartMatch AI — Document Similarity Checker",
  "engine": "Scikit-Learn TF-IDF + Cosine Similarity",
  "supported_formats": [".pdf", ".docx", ".txt"]
}
```

### 2. `GET /api/samples`
Returns the list of preloaded educational documents.

### 3. `POST /api/analyze`
Core similarity analysis endpoint.
- **Request (Multipart Form Data)**:
  - `text` (string): The user's question or search statement.
  - `file` (file): Uploaded `.pdf`, `.docx`, or `.txt` file.
  - *OR* `sample_filename` (string): Preloaded sample file name.
- **Response (JSON)**:
```json
{
  "status": "success",
  "match_found": true,
  "question": "What are the main causes of diabetes?",
  "answer": "What are the main causes of diabetes? The primary causes of diabetes depend on the specific classification. Type 1 diabetes is primarily caused by an autoimmune reaction...",
  "similarity_score": 0.2711,
  "similarity_percentage": 27.1,
  "confidence_label": "Moderate Similarity",
  "source_document": "diabetes_causes.txt",
  "total_paragraphs_compared": 6,
  "best_paragraph_index": 3,
  "matched_terms": ["causes", "diabetes", "main"],
  "algorithm": "Scikit-Learn TF-IDF + Cosine Metric"
}
```

---

## 🎓 College Viva / Presentation Q&A

**Q1: Why use TF-IDF instead of simple word counting?**  
*Answer:* Word counting biases towards common filler words like *"is"*, *"the"*, and *"and"*. TF-IDF incorporates Inverse Document Frequency, penalizing ubiquitous words and emphasizing distinctive, meaningful subject terms.

**Q2: Why use Cosine Similarity instead of Euclidean Distance?**  
*Answer:* Euclidean distance is heavily distorted by paragraph length (a long paragraph with the same topic would have a large distance). Cosine similarity normalizes vector lengths to unit magnitude, evaluating purely the directional angle $\theta$ regardless of document length.

**Q3: Can the user upload Word documents and PDFs?**  
*Answer:* Yes, the backend uses PyMuPDF (`fitz`) for PDF byte stream extraction and `python-docx` for parsing `.docx` paragraphs and tables.
