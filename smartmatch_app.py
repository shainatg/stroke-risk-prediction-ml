"""
================================================================================
  SmartMatch AI — Document Similarity Checker (Single-File Complete Edition)
================================================================================

How to Run in VS Code:
1. Open this file in VS Code (`smartmatch_app.py`).
2. Open terminal in VS Code (Ctrl + ` or Terminal > New Terminal).
3. Ensure required packages are installed:
       pip install flask scikit-learn PyMuPDF python-docx
4. Run this file:
       python smartmatch_app.py
5. Your web browser will automatically open: http://127.0.0.1:5050

Technology Stack:
- Backend: Python + Flask
- Machine Learning & NLP: Scikit-learn (TfidfVectorizer & cosine_similarity)
- Document Extraction: PyMuPDF (PDF), python-docx (Word .docx), UTF-8 (Text .txt)
- Frontend: Single-page application with modern White & Light-Blue theme,
            Tailwind CSS, Lucide icons, responsive layout, and animations.
================================================================================
"""

import os
import sys
import io
import re
import math
import webbrowser
from threading import Timer
from typing import List, Dict, Any

from flask import Flask, request, jsonify, render_template_string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ------------------------------------------------------------------------------
# 1. DOCUMENT EXTRACTION MODULE (PDF, DOCX, TXT)
# ------------------------------------------------------------------------------

# Try PyMuPDF (fitz), with fallback to pypdf
try:
    import pymupdf as fitz
except ImportError:
    try:
        import fitz
    except ImportError:
        fitz = None

try:
    import pypdf
except ImportError:
    pypdf = None

# Try python-docx
try:
    import docx
except ImportError:
    docx = None


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extracts text from PDF bytes using PyMuPDF (fitz) or pypdf."""
    extracted = []
    if fitz is not None:
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            for page in doc:
                text = page.get_text("text")
                if text and text.strip():
                    extracted.append(text.strip())
            doc.close()
            if extracted:
                return "\n\n".join(extracted)
        except Exception:
            pass

    if pypdf is not None:
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        for page in reader.pages:
            text = page.extract_text()
            if text and text.strip():
                extracted.append(text.strip())
        if extracted:
            return "\n\n".join(extracted)

    raise ValueError("Could not extract readable text from PDF.")


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extracts text from Microsoft Word (.docx) paragraphs and tables."""
    if docx is None:
        raise ImportError("python-docx is required. Run: pip install python-docx")

    doc = docx.Document(io.BytesIO(file_bytes))
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text and p.text.strip()]
    for table in doc.tables:
        for row in table.rows:
            row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
            if row_text:
                paragraphs.append(row_text)

    if not paragraphs:
        raise ValueError("The Word document is empty or contains no readable text.")
    return "\n\n".join(paragraphs)


def extract_text_from_txt(file_bytes: bytes) -> str:
    """Extracts text from plain text (.txt) with robust encoding detection."""
    for enc in ["utf-8", "utf-8-sig", "latin-1", "cp1252"]:
        try:
            text = file_bytes.decode(enc)
            if text.strip():
                return text.strip()
        except UnicodeDecodeError:
            continue
    raise ValueError("Could not decode text file.")


def extract_document_text(file_bytes: bytes, filename: str) -> str:
    """Dispatches text extraction based on file extension."""
    name = filename.lower()
    if name.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    elif name.endswith(".docx"):
        return extract_text_from_docx(file_bytes)
    elif name.endswith(".txt"):
        return extract_text_from_txt(file_bytes)
    else:
        raise ValueError(f"Unsupported file type for '{filename}'. Please upload .pdf, .docx, or .txt.")


def split_into_paragraphs(raw_text: str, min_words: int = 5) -> List[Dict[str, Any]]:
    """Splits raw text into logical semantic paragraphs or chunks."""
    text = raw_text.replace("\r\n", "\n").replace("\r", "\n")
    raw_blocks = re.split(r"\n\s*\n+", text)
    paragraphs = []
    current_index = 1

    for block in raw_blocks:
        cleaned = re.sub(r"\s+", " ", block).strip()
        words = cleaned.split()
        if len(words) >= min_words:
            paragraphs.append({
                "index": current_index,
                "text": cleaned,
                "word_count": len(words)
            })
            current_index += 1

    # Fallback if document has no double line breaks
    if len(paragraphs) <= 1 and len(raw_text.split()) > 40:
        sentences = re.split(r"(?<=[.!?])\s+", text)
        chunk = []
        words_count = 0
        current_index = 1
        paragraphs = []
        for s in sentences:
            s_clean = s.strip()
            if not s_clean:
                continue
            w = len(s_clean.split())
            chunk.append(s_clean)
            words_count += w
            if words_count >= 35:
                paragraphs.append({
                    "index": current_index,
                    "text": " ".join(chunk),
                    "word_count": words_count
                })
                current_index += 1
                chunk = []
                words_count = 0
        if chunk:
            paragraphs.append({
                "index": current_index,
                "text": " ".join(chunk),
                "word_count": words_count
            })

    return paragraphs


# ------------------------------------------------------------------------------
# 2. MACHINE LEARNING & NLP SIMILARITY ENGINE
# ------------------------------------------------------------------------------

def compute_tfidf_similarity(query: str, paragraphs: List[Dict[str, Any]], top_k: int = 3) -> Dict[str, Any]:
    """
    Computes text similarity using Scikit-Learn TfidfVectorizer and cosine_similarity.
    
    Formula:
        TF-IDF(t, d, D) = TF(t, d) * log( N / DF(t) )
        Cosine Similarity = (A . B) / (||A|| * ||B||)
    """
    if not paragraphs:
        return {"has_match": False, "best_match": None, "top_score": 0.0, "top_percentage": 0.0}

    doc_texts = [p["text"] for p in paragraphs]
    corpus = [query] + doc_texts

    # 1. Transform texts into TF-IDF matrix
    vectorizer = TfidfVectorizer(
        stop_words="english",
        lowercase=True,
        ngram_range=(1, 2),
        sublinear_tf=True
    )

    try:
        tfidf_matrix = vectorizer.fit_transform(corpus)
    except ValueError:
        vectorizer = TfidfVectorizer(lowercase=True, ngram_range=(1, 1))
        tfidf_matrix = vectorizer.fit_transform(corpus)

    # 2. Compute Cosine Similarities between query (index 0) and paragraphs (1..N)
    query_vector = tfidf_matrix[0:1]
    para_vectors = tfidf_matrix[1:]
    scores = cosine_similarity(query_vector, para_vectors)[0]
    feature_names = vectorizer.get_feature_names_out()

    ranked = []
    for idx, score in enumerate(scores):
        raw_score = float(score)
        
        # Identify top matching keywords
        q_dense = query_vector.toarray()[0]
        p_dense = para_vectors[idx].toarray()[0]
        products = q_dense * p_dense
        top_terms_idx = products.argsort()[::-1][:5]
        matched_terms = [feature_names[i] for i in top_terms_idx if products[i] > 0.0]

        p_info = paragraphs[idx]
        ranked.append({
            "index": p_info["index"],
            "text": p_info["text"],
            "word_count": p_info["word_count"],
            "similarity_score": round(raw_score, 4),
            "similarity_percentage": round(raw_score * 100, 1),
            "matched_terms": matched_terms
        })

    ranked.sort(key=lambda x: x["similarity_score"], reverse=True)
    best_match = ranked[0] if ranked else None
    top_score = best_match["similarity_score"] if best_match else 0.0
    top_percentage = best_match["similarity_percentage"] if best_match else 0.0

    if top_score >= 0.50:
        confidence_label = "High Similarity"
    elif top_score >= 0.20:
        confidence_label = "Moderate Similarity"
    elif top_score > 0.05:
        confidence_label = "Low Similarity"
    else:
        confidence_label = "No Direct Match Found"

    return {
        "has_match": top_score > 0.05,
        "best_match": best_match,
        "top_score": top_score,
        "top_percentage": top_percentage,
        "confidence_label": confidence_label,
        "total_paragraphs_compared": len(paragraphs),
        "candidates": ranked[:top_k],
        "algorithm": "Scikit-Learn TF-IDF + Cosine Metric"
    }


# ------------------------------------------------------------------------------
# 3. BUILT-IN EDUCATIONAL SAMPLE DOCUMENTS
# ------------------------------------------------------------------------------

SAMPLE_DOCUMENTS = {
    "diabetes_causes.txt": {
        "title": "Clinical Overview of Diabetes Mellitus",
        "suggested_query": "What are the main causes of diabetes?",
        "content": """Diabetes mellitus is a chronic metabolic disorder characterized by elevated levels of blood glucose over a prolonged period. The disease results from either insufficient insulin production by pancreatic beta cells, or the body cells failing to respond appropriately to the insulin produced.

What are the main causes of diabetes?
The primary causes of diabetes depend on the specific classification. Type 1 diabetes is primarily caused by an autoimmune reaction where the immune system mistakenly attacks and destroys insulin-producing beta cells in the islet of Langerhans within the pancreas. Genetic susceptibility, human leukocyte antigen (HLA) genotypes, and environmental triggers such as viral infections are significant contributing factors.

In contrast, Type 2 diabetes develops from a combination of chronic insulin resistance and progressive secretory deficiency. The predominant risk factors and root causes include prolonged obesity, physical inactivity, atherogenic diets high in refined sugars and saturated fats, advancing age, and strong familial genetic predispositions. Chronic low-grade systemic inflammation and visceral adiposity disrupt insulin signaling pathways in hepatic, muscular, and adipose tissues.

Gestational diabetes occurs during pregnancy when placental hormones impair maternal insulin sensitivity, causing blood glucose levels to elevate beyond normal thresholds.

Management and therapeutic interventions include regular physical aerobic activity, balanced carbohydrate-controlled nutrition, continuous glucose monitoring, oral antihyperglycemic pharmacotherapy such as metformin and SGLT2 inhibitors, and exogenous subcutaneous insulin replacement when indicated."""
    },
    "artificial_intelligence.txt": {
        "title": "Fundamentals of AI & Natural Language Processing",
        "suggested_query": "How does TF-IDF and cosine similarity work in NLP?",
        "content": """Artificial intelligence (AI) is the simulation of human intelligence processes by computer systems, including learning, reasoning, and self-correction.

Natural Language Processing (NLP) is a specialized branch of artificial intelligence focused on enabling computers to understand, interpret, and manipulate human language. Core NLP tasks include text classification, sentiment analysis, named entity recognition, and semantic similarity measurement using vector space models.

Term Frequency-Inverse Document Frequency (TF-IDF) is a foundational statistical method in NLP. It evaluates how important a word is to a document within a larger collection. Words that appear frequently in a specific paragraph but rarely across the rest of the document receive the highest mathematical weights.

Cosine similarity evaluates the orientation rather than magnitude between two multi-dimensional numerical vectors. By calculating the cosine of the angle between query and document vectors, systems can retrieve the most relevant passages regardless of paragraph length."""
    },
    "climate_change.txt": {
        "title": "Global Climate Dynamics & Renewable Energy",
        "suggested_query": "What are the primary drivers of global warming and climate change?",
        "content": """Climate change refers to long-term shifts in temperatures and weather patterns across the Earth's biosphere. While natural processes influence the climate, human industrial activities have been the primary driver of global warming since the mid-19th century.

The combustion of fossil fuels—coal, oil, and gas—releases billions of metric tons of carbon dioxide and nitrous oxide into the atmosphere. These heat-trapping greenhouse gases blanket the Earth, preventing thermal radiation from escaping into space and elevating average global temperatures.

Consequences of rapid climate change include intensifying droughts, water scarcity, catastrophic wildfires, rising global sea levels from melting polar ice sheets, and the loss of biodiversity across marine coral reefs.

Transitioning from fossil fuels to clean renewable energy sources such as utility-scale solar photovoltaics, wind turbines, geothermal energy, and green hydrogen represents the cornerstone of international decarbonization commitments."""
    }
}


# ------------------------------------------------------------------------------
# 4. SINGLE-PAGE APPLICATION HTML/CSS/JAVASCRIPT TEMPLATE
# ------------------------------------------------------------------------------

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SmartMatch AI — Document Similarity Checker</title>
  <!-- Google Fonts: Inter -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  <!-- Tailwind CSS CDN -->
  <script src="https://cdn.tailwindcss.com"></script>
  <!-- Lucide Icons CDN -->
  <script src="https://unpkg.com/lucide@latest"></script>
  <style>
    body { font-family: 'Inter', system-ui, -apple-system, sans-serif; }
    .card-soft {
      background: #ffffff;
      border: 1px solid rgba(186, 226, 253, 0.7);
      box-shadow: 0 4px 20px -2px rgba(14, 165, 233, 0.06), 0 2px 6px -1px rgba(0, 0, 0, 0.04);
      transition: all 0.2s ease;
    }
    .card-soft:hover {
      border-color: rgba(56, 174, 249, 0.85);
      box-shadow: 0 10px 25px -4px rgba(14, 165, 233, 0.12);
    }
  </style>
</head>
<body class="bg-gradient-to-b from-[#f8fafc] via-[#f0f7ff] to-[#e6f2fd] text-slate-800 min-h-screen flex flex-col justify-between">

  <!-- Header -->
  <header class="w-full pt-8 pb-6 px-4">
    <div class="max-w-5xl mx-auto text-center">
      <div class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-sky-100/90 border border-sky-200 text-sky-800 text-xs font-semibold uppercase tracking-wider mb-4 shadow-sm">
        <i data-lucide="sparkles" class="w-3.5 h-3.5 text-sky-600"></i>
        <span>NLP & Text Similarity Studio</span>
        <span class="w-1 h-1 rounded-full bg-sky-400"></span>
        <span class="text-sky-600">Single-File Edition</span>
      </div>

      <h1 class="text-4xl sm:text-5xl font-extrabold text-slate-900 tracking-tight mb-3">
        SmartMatch <span class="text-transparent bg-clip-text bg-gradient-to-r from-sky-600 to-blue-700">AI</span>
      </h1>

      <p class="text-lg sm:text-xl text-slate-600 max-w-2xl mx-auto font-normal">
        Upload a document, ask a question, and find the most relevant answer.
      </p>

      <div class="mt-4 flex flex-wrap items-center justify-center gap-2 text-xs text-slate-600">
        <span class="inline-flex items-center gap-1.5 px-3 py-1 bg-white rounded-lg border border-sky-100 shadow-xs font-medium">
          <i data-lucide="cpu" class="w-3.5 h-3.5 text-sky-600"></i> Scikit-Learn TF-IDF
        </span>
        <span class="inline-flex items-center gap-1.5 px-3 py-1 bg-white rounded-lg border border-sky-100 shadow-xs font-medium">
          <i data-lucide="compass" class="w-3.5 h-3.5 text-blue-600"></i> Cosine Similarity Vector Space
        </span>
        <span class="inline-flex items-center gap-1.5 px-3 py-1 bg-white rounded-lg border border-sky-100 shadow-xs font-medium">
          <i data-lucide="file-text" class="w-3.5 h-3.5 text-emerald-600"></i> PDF + DOCX + TXT
        </span>
        <button onclick="toggleModal(true)" class="inline-flex items-center gap-1.5 px-3 py-1 bg-sky-600 hover:bg-sky-700 text-white rounded-lg font-medium transition-colors shadow-xs cursor-pointer">
          <i data-lucide="book-open" class="w-3.5 h-3.5"></i> How Similarity Works
        </button>
      </div>
    </div>
  </header>

  <!-- Main Content Container -->
  <main class="max-w-5xl mx-auto px-4 pb-12 w-full">
    
    <!-- Top Input Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 items-start">
      
      <!-- 1. Text Input Section -->
      <div class="card-soft rounded-2xl p-6">
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center gap-2">
            <div class="w-8 h-8 rounded-lg bg-sky-100 flex items-center justify-center text-sky-700">
              <i data-lucide="help-circle" class="w-4 h-4"></i>
            </div>
            <div>
              <h2 class="text-lg font-bold text-slate-900">Enter Your Question or Text</h2>
              <p class="text-xs text-slate-500">Ask anything or enter keywords to match</p>
            </div>
          </div>
          <button id="clearBtn" onclick="clearText()" class="hidden inline-flex items-center gap-1 px-2.5 py-1 text-xs font-medium text-slate-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors cursor-pointer">
            <i data-lucide="x-circle" class="w-3.5 h-3.5"></i> Clear
          </button>
        </div>

        <textarea id="questionInput" rows="4"
          placeholder="Example: What are the main causes of diabetes?"
          oninput="handleTextInput()"
          class="w-full p-4 rounded-xl text-slate-800 placeholder-slate-400 bg-slate-50/70 border border-slate-200 focus:bg-white focus:outline-none focus:ring-2 focus:ring-sky-100 focus:border-sky-500 transition-all resize-none text-sm sm:text-base leading-relaxed"></textarea>

        <div class="flex items-center justify-between mt-2 px-1 text-xs text-slate-400">
          <span id="wordCount">0 words</span>
          <span id="charCount">0 characters</span>
        </div>

        <div id="errorText" class="hidden mt-3 p-3 bg-red-50 border border-red-200 rounded-xl text-xs text-red-700 flex items-center gap-2">
          <i data-lucide="alert-circle" class="w-4 h-4 text-red-600"></i>
          <span id="errorTextMessage">Please enter your question or text in the text box.</span>
        </div>

        <!-- Sample question chips -->
        <div class="mt-4 pt-4 border-t border-slate-100">
          <div class="flex items-center gap-1.5 text-xs text-slate-500 mb-2 font-medium">
            <i data-lucide="lightbulb" class="w-3.5 h-3.5 text-amber-500"></i>
            <span>Try a sample question:</span>
          </div>
          <div class="flex flex-wrap gap-1.5">
            <button onclick="setQuery('What are the main causes of diabetes?')" class="text-xs px-2.5 py-1 rounded-lg bg-sky-50 hover:bg-sky-100 text-sky-800 border border-sky-200 transition-colors text-left">
              "What are the main causes of diabetes?"
            </button>
            <button onclick="setQuery('How does TF-IDF and cosine similarity work in NLP?')" class="text-xs px-2.5 py-1 rounded-lg bg-sky-50 hover:bg-sky-100 text-sky-800 border border-sky-200 transition-colors text-left">
              "How does TF-IDF and cosine similarity work in NLP?"
            </button>
            <button onclick="setQuery('What are the primary drivers of global warming and climate change?')" class="text-xs px-2.5 py-1 rounded-lg bg-sky-50 hover:bg-sky-100 text-sky-800 border border-sky-200 transition-colors text-left">
              "What are the primary drivers of global warming?"
            </button>
          </div>
        </div>
      </div>

      <!-- 2. File Upload Section -->
      <div class="card-soft rounded-2xl p-6">
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center gap-2">
            <div class="w-8 h-8 rounded-lg bg-sky-100 flex items-center justify-center text-sky-700">
              <i data-lucide="upload-cloud" class="w-4 h-4"></i>
            </div>
            <div>
              <h2 class="text-lg font-bold text-slate-900">Upload Your Document</h2>
              <p class="text-xs text-slate-500">PDF (.pdf), Word (.docx), or Text (.txt)</p>
            </div>
          </div>
          <span class="text-[11px] font-medium text-slate-500 bg-slate-100 px-2 py-0.5 rounded border">
            Up to 16 MB
          </span>
        </div>

        <input type="file" id="fileInput" accept=".pdf,.docx,.txt" class="hidden" onchange="handleFileSelected(this.files)">

        <!-- Dropzone -->
        <div id="dropZone"
             onclick="document.getElementById('fileInput').click()"
             ondragover="handleDragOver(event)"
             ondragleave="handleDragLeave(event)"
             ondrop="handleDrop(event)"
             class="border-2 border-dashed border-sky-200 bg-sky-50/40 hover:border-sky-400 hover:bg-sky-50/70 rounded-xl p-6 text-center cursor-pointer transition-all">
          <div class="w-12 h-12 rounded-2xl bg-white border border-sky-100 shadow-xs mx-auto flex items-center justify-center text-sky-600 mb-2">
            <i data-lucide="upload-cloud" class="w-6 h-6"></i>
          </div>
          <p class="text-sm font-semibold text-slate-800">
            <span class="text-sky-600 hover:underline">Click to browse</span> or drag & drop file
          </p>
          <p class="text-xs text-slate-500 mt-0.5">Supports PDF, DOCX, TXT</p>
          <button type="button" class="mt-3 inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-sky-700 bg-white border border-sky-200 rounded-lg shadow-xs">
            <i data-lucide="folder-open" class="w-3.5 h-3.5 text-sky-600"></i> Browse Files
          </button>
        </div>

        <!-- File Active Card -->
        <div id="activeFileCard" class="hidden p-4 rounded-xl bg-sky-50 border border-sky-200 flex items-center justify-between">
          <div class="flex items-center gap-3 truncate">
            <div class="w-10 h-10 rounded-xl bg-white border border-sky-200 flex items-center justify-center text-sky-600 shrink-0">
              <i data-lucide="file-text" class="w-5 h-5"></i>
            </div>
            <div class="truncate">
              <p id="activeFileName" class="text-sm font-bold text-slate-900 truncate"></p>
              <p id="activeFileSize" class="text-xs text-slate-500 mt-0.5"></p>
            </div>
          </div>
          <div class="flex items-center gap-1.5 shrink-0">
            <button onclick="document.getElementById('fileInput').click()" class="px-2.5 py-1 text-xs font-semibold text-sky-700 bg-white border border-sky-300 rounded-lg hover:bg-sky-50">
              Replace
            </button>
            <button onclick="removeFile()" class="p-1 text-red-600 hover:bg-red-50 rounded-lg" title="Remove file">
              <i data-lucide="x-circle" class="w-4 h-4"></i>
            </button>
          </div>
        </div>

        <div id="errorFile" class="hidden mt-3 p-3 bg-red-50 border border-red-200 rounded-xl text-xs text-red-700 flex items-center gap-2">
          <i data-lucide="alert-circle" class="w-4 h-4 text-red-600"></i>
          <span>Please upload a document or choose a sample file below.</span>
        </div>

        <!-- 1-Click Samples -->
        <div class="mt-4 pt-4 border-t border-slate-100">
          <p class="text-xs font-medium text-slate-600 mb-2">No file handy? Pick a preloaded sample:</p>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-2">
            <button onclick="pickSample('diabetes_causes.txt')" class="sample-btn p-2 rounded-xl border border-slate-200 hover:border-sky-300 hover:bg-sky-50 text-left text-xs font-medium text-slate-700 truncate">
              diabetes_causes.txt
            </button>
            <button onclick="pickSample('artificial_intelligence.txt')" class="sample-btn p-2 rounded-xl border border-slate-200 hover:border-sky-300 hover:bg-sky-50 text-left text-xs font-medium text-slate-700 truncate">
              ai_overview.txt
            </button>
            <button onclick="pickSample('climate_change.txt')" class="sample-btn p-2 rounded-xl border border-slate-200 hover:border-sky-300 hover:bg-sky-50 text-left text-xs font-medium text-slate-700 truncate">
              climate_change.txt
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 3. Analyze Action Button -->
    <div class="mt-8 text-center">
      <button id="analyzeBtn" onclick="runAnalysis()" class="w-full sm:w-auto min-w-[320px] px-8 py-4 rounded-2xl font-bold text-base transition-all duration-200 flex items-center justify-center gap-3 shadow-md mx-auto cursor-pointer bg-gradient-to-r from-sky-600 via-blue-600 to-indigo-600 hover:from-sky-500 hover:to-indigo-500 text-white shadow-sky-500/25 hover:shadow-lg hover:-translate-y-0.5">
        <i data-lucide="sparkles" class="w-5 h-5 text-sky-200"></i>
        <span id="analyzeBtnText">Find Similarity & Generate Answer</span>
        <i data-lucide="arrow-right" class="w-5 h-5 text-white/80"></i>
      </button>
      <p class="text-xs text-slate-400 mt-2">Calculates Scikit-Learn TF-IDF paragraph vectors & cosine similarity in real-time</p>
    </div>

    <!-- 4. Results Section -->
    <div id="resultsCard" class="hidden mt-8">
      <div class="card-soft rounded-3xl p-6 sm:p-8 bg-white border border-sky-200 shadow-xl">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-6 border-b border-slate-100">
          <div class="flex items-center gap-2.5">
            <div class="w-10 h-10 rounded-2xl bg-sky-50 border border-sky-200 flex items-center justify-center text-sky-600">
              <i data-lucide="sparkles" class="w-5 h-5"></i>
            </div>
            <div>
              <span class="text-xs font-semibold text-sky-600 uppercase tracking-wider">Analysis Complete</span>
              <h2 class="text-2xl font-extrabold text-slate-900">Document Similarity Result</h2>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <button onclick="copyAnswer()" class="inline-flex items-center gap-1.5 px-3.5 py-2 text-xs font-bold text-slate-700 bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded-xl transition-all cursor-pointer">
              <i data-lucide="copy" class="w-4 h-4 text-slate-500"></i>
              <span id="copyBtnText">Copy Answer</span>
            </button>
            <button onclick="analyzeAgain()" class="inline-flex items-center gap-1.5 px-3.5 py-2 text-xs font-bold text-white bg-sky-600 hover:bg-sky-700 rounded-xl transition-all cursor-pointer">
              <i data-lucide="rotate-ccw" class="w-3.5 h-3.5"></i>
              <span>Analyze Again</span>
            </button>
          </div>
        </div>

        <!-- Your Question -->
        <div class="mt-6 p-4 rounded-2xl bg-slate-50 border border-slate-200">
          <p class="text-xs font-bold uppercase tracking-wider text-slate-500 mb-1">Your Question</p>
          <p id="resultQuestion" class="text-base sm:text-lg font-semibold text-slate-900"></p>
        </div>

        <!-- Most Relevant Answer -->
        <div class="mt-4 p-5 rounded-2xl bg-sky-50/50 border border-sky-100">
          <div class="flex items-center justify-between mb-2">
            <p class="text-xs font-bold uppercase tracking-wider text-sky-700 flex items-center gap-1.5">
              <i data-lucide="file-text" class="w-3.5 h-3.5 text-sky-600"></i>
              Most Relevant Answer
              <span id="resultParaIdx" class="text-[11px] font-normal text-slate-500"></span>
            </p>
            <span id="resultMatchedTerms" class="text-[11px] text-slate-500"></span>
          </div>
          <p id="resultAnswer" class="text-base text-slate-800 leading-relaxed whitespace-pre-wrap"></p>
        </div>

        <!-- Similarity Score & Source Document Grid -->
        <div class="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="p-4 rounded-2xl bg-white border border-slate-200">
            <div class="flex items-center justify-between mb-1">
              <span class="text-xs font-bold uppercase tracking-wider text-slate-500">Similarity Score</span>
              <span id="resultConfidence" class="text-xs font-bold px-2 py-0.5 rounded-full border bg-sky-50 text-sky-700 border-sky-200"></span>
            </div>
            <div class="flex items-baseline gap-2 mb-2">
              <span id="resultPercentage" class="text-3xl font-extrabold text-slate-900">0%</span>
              <span id="resultCosine" class="text-xs text-slate-500 font-mono"></span>
            </div>
            <div class="w-full h-3 rounded-full bg-slate-100 overflow-hidden border border-slate-200 p-0.5">
              <div id="resultProgressBar" class="h-full rounded-full bg-gradient-to-r from-sky-500 to-blue-600 transition-all duration-700" style="width: 0%"></div>
            </div>
          </div>

          <div class="p-4 rounded-2xl bg-white border border-slate-200 flex flex-col justify-between">
            <div>
              <span class="text-xs font-bold uppercase tracking-wider text-slate-500">Source Document</span>
              <p id="resultDocument" class="text-sm font-bold text-slate-900 truncate mt-1"></p>
            </div>
            <div class="flex items-center justify-between text-xs text-slate-500 pt-2 border-t border-slate-100 mt-2">
              <span id="resultParagraphsCount"></span>
              <span class="text-sky-600 font-medium">Scikit-Learn TF-IDF</span>
            </div>
          </div>
        </div>

        <!-- Educational Note -->
        <div class="mt-4 p-3.5 rounded-xl bg-amber-50 border border-amber-200 text-xs text-amber-900 flex items-start gap-2.5">
          <i data-lucide="info" class="w-4 h-4 text-amber-600 shrink-0 mt-0.5"></i>
          <div>
            <span class="font-bold">Understanding Your Similarity Score: </span>
            This score measures <em>textual vector alignment</em> using Scikit-Learn TF-IDF and Cosine Similarity. It indicates how closely vocabulary terms overlap, not the scientific probability that the source answer is correct.
          </div>
        </div>
      </div>
    </div>

    <!-- 5. 4-Step Workflow Section -->
    <section class="w-full mt-14 pt-8 pb-4 border-t border-sky-100">
      <div class="text-center mb-6">
        <span class="text-xs font-bold text-sky-600 uppercase tracking-widest">Simple 4-Step Workflow</span>
        <h3 class="text-2xl font-bold text-slate-900 mt-1">How SmartMatch AI Works</h3>
        <p class="text-xs text-slate-500 mt-0.5">Enter Text &rarr; Upload File &rarr; Analyze Similarity &rarr; Get Answer</p>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="card-soft rounded-2xl p-5 bg-white border border-sky-100">
          <div class="w-10 h-10 rounded-xl bg-sky-50 border border-sky-200 flex items-center justify-center text-sky-600 mb-3">
            <i data-lucide="edit-3" class="w-5 h-5"></i>
          </div>
          <h4 class="text-base font-bold text-slate-900 mb-1">01. Enter Text</h4>
          <p class="text-xs text-slate-500">Type any question, statement, or paragraph you want to search.</p>
        </div>

        <div class="card-soft rounded-2xl p-5 bg-white border border-sky-100">
          <div class="w-10 h-10 rounded-xl bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-600 mb-3">
            <i data-lucide="upload-cloud" class="w-5 h-5"></i>
          </div>
          <h4 class="text-base font-bold text-slate-900 mb-1">02. Upload File</h4>
          <p class="text-xs text-slate-500">Upload your PDF, Word (.docx), or plain text document.</p>
        </div>

        <div class="card-soft rounded-2xl p-5 bg-white border border-sky-100">
          <div class="w-10 h-10 rounded-xl bg-indigo-50 border border-indigo-200 flex items-center justify-center text-indigo-600 mb-3">
            <i data-lucide="cpu" class="w-5 h-5"></i>
          </div>
          <h4 class="text-base font-bold text-slate-900 mb-1">03. Analyze Similarity</h4>
          <p class="text-xs text-slate-500">Scikit-learn transforms text into TF-IDF vectors and computes cosine angle.</p>
        </div>

        <div class="card-soft rounded-2xl p-5 bg-white border border-sky-100">
          <div class="w-10 h-10 rounded-xl bg-emerald-50 border border-emerald-200 flex items-center justify-center text-emerald-600 mb-3">
            <i data-lucide="check-circle-2" class="w-5 h-5"></i>
          </div>
          <h4 class="text-base font-bold text-slate-900 mb-1">04. Get Answer</h4>
          <p class="text-xs text-slate-500">View the highest-matching paragraph and actual similarity percentage.</p>
        </div>
      </div>
    </section>
  </main>

  <!-- Educational Theory Modal -->
  <div id="theoryModal" class="hidden fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-xs">
    <div class="bg-white rounded-3xl max-w-xl w-full p-6 sm:p-8 shadow-2xl border border-sky-100 max-h-[90vh] overflow-y-auto">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-bold text-slate-900 flex items-center gap-2">
          <i data-lucide="book-open" class="w-5 h-5 text-sky-600"></i> How Text Similarity Works
        </h3>
        <button onclick="toggleModal(false)" class="p-1 text-slate-400 hover:text-slate-700">
          <i data-lucide="x" class="w-5 h-5"></i>
        </button>
      </div>

      <div class="space-y-4 text-xs text-slate-600 leading-relaxed">
        <div class="p-3 bg-slate-50 rounded-xl border border-slate-200">
          <strong class="text-slate-900 block mb-1">1. TF-IDF Numerical Vectorization:</strong>
          TF-IDF(t, d) = TF(t, d) &times; log( N / DF(t) )<br>
          Gives higher mathematical weights to rare, meaningful keywords (e.g. <em>"diabetes"</em>) and lowers common filler words (e.g. <em>"the", "is"</em>).
        </div>

        <div class="p-3 bg-sky-50 rounded-xl border border-sky-200">
          <strong class="text-slate-900 block mb-1">2. Cosine Similarity Formula:</strong>
          Cosine Similarity = (A &sdot; B) / ( ||A|| &times; ||B|| )<br>
          Measures the directional angle between query vector A and paragraph vector B in multi-dimensional space, returning a score from 0.0 (no overlap) to 1.0 (identical).
        </div>
      </div>

      <div class="mt-6 text-right">
        <button onclick="toggleModal(false)" class="px-4 py-2 bg-sky-600 text-white rounded-xl font-semibold text-xs hover:bg-sky-700">
          Close Window
        </button>
      </div>
    </div>
  </div>

  <!-- Footer -->
  <footer class="w-full py-4 text-center text-xs text-slate-500 border-t border-sky-100 bg-white/60">
    <strong>SmartMatch AI</strong> • Built with Python, Flask, Scikit-learn, PyMuPDF & python-docx
  </footer>

  <!-- Client-side Logic -->
  <script>
    let activeFile = null;
    let activeSampleName = null;
    let latestAnswer = "";

    function handleTextInput() {
      const text = document.getElementById('questionInput').value;
      const chars = text.length;
      const words = text.trim() ? text.trim().split(/\\s+/).length : 0;
      document.getElementById('charCount').innerText = `${chars} characters`;
      document.getElementById('wordCount').innerText = `${words} words`;
      document.getElementById('clearBtn').classList.toggle('hidden', text.length === 0);
      document.getElementById('errorText').classList.add('hidden');
    }

    function clearText() {
      document.getElementById('questionInput').value = '';
      handleTextInput();
    }

    function setQuery(q) {
      document.getElementById('questionInput').value = q;
      handleTextInput();
    }

    function handleFileSelected(files) {
      if (files && files.length > 0) {
        activeFile = files[0];
        activeSampleName = null;
        showActiveFile(activeFile.name, (activeFile.size / 1024).toFixed(1) + ' KB');
      }
    }

    function pickSample(name) {
      activeFile = null;
      activeSampleName = name;
      showActiveFile(name, 'Preloaded Sample Document');
      if (name.includes('diabetes')) setQuery('What are the main causes of diabetes?');
      else if (name.includes('ai')) setQuery('How does TF-IDF and cosine similarity work in NLP?');
      else if (name.includes('climate')) setQuery('What are the primary drivers of global warming and climate change?');
    }

    function showActiveFile(name, size) {
      document.getElementById('dropZone').classList.add('hidden');
      document.getElementById('activeFileCard').classList.remove('hidden');
      document.getElementById('activeFileName').innerText = name;
      document.getElementById('activeFileSize').innerText = size;
      document.getElementById('errorFile').classList.add('hidden');
    }

    function removeFile() {
      activeFile = null;
      activeSampleName = null;
      document.getElementById('fileInput').value = '';
      document.getElementById('dropZone').classList.remove('hidden');
      document.getElementById('activeFileCard').classList.add('hidden');
    }

    function handleDragOver(e) { e.preventDefault(); }
    function handleDragLeave(e) { e.preventDefault(); }
    function handleDrop(e) {
      e.preventDefault();
      if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        handleFileSelected(e.dataTransfer.files);
      }
    }

    async function runAnalysis() {
      const text = document.getElementById('questionInput').value.trim();
      let hasError = false;

      if (!text) {
        document.getElementById('errorText').classList.remove('hidden');
        hasError = true;
      }
      if (!activeFile && !activeSampleName) {
        document.getElementById('errorFile').classList.remove('hidden');
        hasError = true;
      }
      if (hasError) return;

      // Loading state
      const btn = document.getElementById('analyzeBtn');
      const btnText = document.getElementById('analyzeBtnText');
      btn.disabled = true;
      btnText.innerText = 'Analyzing your document...';

      const formData = new FormData();
      formData.append('text', text);
      if (activeFile) formData.append('file', activeFile);
      else if (activeSampleName) formData.append('sample_filename', activeSampleName);

      try {
        const response = await fetch('/api/analyze', { method: 'POST', body: formData });
        const data = await response.json();
        if (data.status === 'success') {
          displayResult(data);
        } else {
          alert('Error: ' + data.message);
        }
      } catch (err) {
        alert('Could not connect to backend server: ' + err);
      } finally {
        btn.disabled = false;
        btnText.innerText = 'Find Similarity & Generate Answer';
      }
    }

    function displayResult(data) {
      latestAnswer = data.answer;
      document.getElementById('resultsCard').classList.remove('hidden');
      document.getElementById('resultQuestion').innerText = `"${data.question}"`;
      document.getElementById('resultAnswer').innerText = data.answer;
      document.getElementById('resultParaIdx').innerText = data.best_paragraph_index ? `(extracted from paragraph #${data.best_paragraph_index})` : '';
      document.getElementById('resultMatchedTerms').innerText = data.matched_terms.length > 0 ? `Matched terms: ${data.matched_terms.slice(0, 3).join(', ')}` : '';
      document.getElementById('resultConfidence').innerText = data.confidence_label;
      document.getElementById('resultPercentage').innerText = `${data.similarity_percentage}%`;
      document.getElementById('resultCosine').innerText = `(Cosine: ${data.similarity_score})`;
      document.getElementById('resultProgressBar').style.width = `${Math.min(100, Math.max(5, data.similarity_percentage))}%`;
      document.getElementById('resultDocument').innerText = data.source_document;
      document.getElementById('resultParagraphsCount').innerText = `${data.total_paragraphs_compared} paragraphs analyzed`;

      lucide.createIcons();
      document.getElementById('resultsCard').scrollIntoView({ behavior: 'smooth' });
    }

    function copyAnswer() {
      if (latestAnswer) {
        navigator.clipboard.writeText(latestAnswer).then(() => {
          document.getElementById('copyBtnText').innerText = 'Copied!';
          setTimeout(() => { document.getElementById('copyBtnText').innerText = 'Copy Answer'; }, 2000);
        });
      }
    }

    function analyzeAgain() {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    function toggleModal(show) {
      document.getElementById('theoryModal').classList.toggle('hidden', !show);
    }

    window.onload = () => { lucide.createIcons(); };
  </script>
</body>
</html>
"""


# ------------------------------------------------------------------------------
# 5. FLASK REST APPLICATION & ROUTES
# ------------------------------------------------------------------------------

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB limit


@app.route("/", methods=["GET"])
def index():
    """Serves the complete single-page interactive application."""
    return render_template_string(HTML_TEMPLATE)


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "service": "SmartMatch AI — Document Similarity Checker",
        "algorithm": "Scikit-Learn TF-IDF + Cosine Similarity",
        "supported_formats": [".pdf", ".docx", ".txt"]
    })


@app.route("/api/analyze", methods=["POST"])
def analyze():
    # 1. Text input validation
    query = request.form.get("text", "").strip()
    if not query:
        return jsonify({"status": "error", "message": "Please enter a question or text in the text box."}), 400

    # 2. File retrieval
    file_bytes = None
    filename = None

    if "file" in request.files and request.files["file"].filename != "":
        f = request.files["file"]
        filename = f.filename
        file_bytes = f.read()
    elif "sample_filename" in request.form and request.form["sample_filename"].strip():
        sample_key = request.form["sample_filename"].strip()
        if sample_key in SAMPLE_DOCUMENTS:
            filename = sample_key
            file_bytes = SAMPLE_DOCUMENTS[sample_key]["content"].encode("utf-8")
        else:
            return jsonify({"status": "error", "message": f"Sample file '{sample_key}' not found."}), 404
    else:
        return jsonify({"status": "error", "message": "Please upload a document (.pdf, .docx, or .txt)."}), 400

    # 3. Text Extraction
    try:
        raw_text = extract_document_text(file_bytes, filename)
    except Exception as e:
        return jsonify({"status": "error", "message": f"Could not extract text: {str(e)}"}), 422

    # 4. Paragraph Segmentation
    paragraphs = split_into_paragraphs(raw_text)
    if not paragraphs:
        return jsonify({"status": "error", "message": "No substantial paragraphs found in document."}), 422

    # 5. Scikit-Learn TF-IDF & Cosine Similarity
    result = compute_tfidf_similarity(query, paragraphs, top_k=3)
    best_match = result.get("best_match")

    answer = best_match["text"] if (best_match and result["top_score"] > 0.02) else "No matching paragraph found."

    return jsonify({
        "status": "success",
        "match_found": result["has_match"],
        "question": query,
        "answer": answer,
        "similarity_score": result["top_score"],
        "similarity_percentage": result["top_percentage"],
        "confidence_label": result["confidence_label"],
        "source_document": filename,
        "total_paragraphs_compared": len(paragraphs),
        "best_paragraph_index": best_match["index"] if best_match else None,
        "matched_terms": best_match["matched_terms"] if best_match else [],
        "candidates": result.get("candidates", [])
    })


# ------------------------------------------------------------------------------
# 6. MAIN EXECUTION ENTRY POINT
# ------------------------------------------------------------------------------

def open_browser(url: str):
    """Automatically launches the user's default web browser."""
    webbrowser.open_new_tab(url)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    host = "127.0.0.1"
    url = f"http://{host}:{port}"

    print("=" * 75)
    print("       SMARTMATCH AI — DOCUMENT SIMILARITY CHECKER")
    print("=" * 75)
    print(f"  * Web Application URL : {url}")
    print(f"  * Machine Learning    : Scikit-Learn TF-IDF + Cosine Similarity")
    print(f"  * Supported Formats   : PDF (PyMuPDF) + Word (python-docx) + Text (.txt)")
    print("=" * 75)
    print("  Starting Flask server... Press Ctrl+C in terminal to stop.\n")

    # Automatically open browser after 1 second
    Timer(1.0, open_browser, [url]).start()

    # Start Flask Server
    app.run(host=host, port=port, debug=False)
