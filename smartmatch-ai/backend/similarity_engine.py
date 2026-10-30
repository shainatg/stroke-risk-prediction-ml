"""
SmartMatch AI - TF-IDF & Cosine Text Similarity Engine
======================================================
This module implements the natural language processing (NLP) and machine
learning algorithms that compare the user's question with each paragraph
of the uploaded document.

How It Works (College Presentation Guide):
------------------------------------------
1. Term Frequency-Inverse Document Frequency (TF-IDF):
   - Term Frequency (TF): Counts how often a word appears in a paragraph.
   - Inverse Document Frequency (IDF): Gives higher mathematical weight
     to rare, meaningful words (e.g. "diabetes", "insulin") and lowers
     common grammatical filler words ("the", "is", "in").
   - This converts raw text into numerical high-dimensional vector representations.

2. Cosine Similarity Metric:
   - Measures the cosine of the angle theta between the user's query vector
     and each paragraph vector in multi-dimensional space:
     
           Cosine Similarity = (A . B) / (||A|| * ||B||)
           
   - Ranges from 0.0 (completely orthogonal / no similarity) to 1.0 (identical).
   - Multiplied by 100 to yield a clear percentage score (e.g., 78.4%).
"""

import re
import math
from typing import List, Dict, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ==============================================================================
# 1. SCIKIT-LEARN TF-IDF & COSINE SIMILARITY ENGINE (PRIMARY)
# ==============================================================================

def compute_tfidf_similarity(
    query: str,
    paragraphs: List[Dict[str, Any]],
    top_k: int = 3
) -> Dict[str, Any]:
    """
    Computes text similarity using Scikit-Learn's TfidfVectorizer and cosine_similarity.
    
    Parameters:
    - query: The user's input question or statement
    - paragraphs: List of paragraph dictionaries from document_extractor
    - top_k: How many top matching candidates to return
    
    Returns:
    - Dictionary with the best match, top score, and candidate rankings.
    """
    if not paragraphs:
        return {
            "has_match": False,
            "best_match": None,
            "top_score": 0.0,
            "top_percentage": 0.0,
            "candidates": [],
            "message": "The document contains no readable paragraphs to compare."
        }

    # Extract clean text from each paragraph
    doc_texts = [p["text"] for p in paragraphs]
    corpus = [query] + doc_texts

    # Configure Scikit-learn TF-IDF Vectorizer
    # Uses English stop words removal, unigrams + bigrams for phrase matching
    vectorizer = TfidfVectorizer(
        stop_words="english",
        lowercase=True,
        ngram_range=(1, 2),
        sublinear_tf=True
    )

    try:
        tfidf_matrix = vectorizer.fit_transform(corpus)
    except ValueError:
        # Happens if query and document contain only stop words or symbols
        vectorizer = TfidfVectorizer(lowercase=True, ngram_range=(1, 1))
        tfidf_matrix = vectorizer.fit_transform(corpus)

    # Matrix slice 0 is the user's query vector
    query_vector = tfidf_matrix[0:1]
    
    # Slices 1..N are the paragraph vectors
    paragraph_vectors = tfidf_matrix[1:]

    # Calculate cosine similarity matrix (1 x N)
    similarity_matrix = cosine_similarity(query_vector, paragraph_vectors)[0]

    feature_names = vectorizer.get_feature_names_out()

    # Score and rank all candidate paragraphs
    ranked_candidates = []
    for idx, score in enumerate(similarity_matrix):
        raw_score = float(score)
        
        # Identify top overlapping keywords for explainability
        query_dense = query_vector.toarray()[0]
        para_dense = paragraph_vectors[idx].toarray()[0]
        term_products = query_dense * para_dense
        top_term_indices = term_products.argsort()[::-1][:5]
        
        matched_terms = [
            feature_names[i]
            for i in top_term_indices
            if term_products[i] > 0.0
        ]

        p_info = paragraphs[idx]
        ranked_candidates.append({
            "index": p_info["index"],
            "text": p_info["text"],
            "word_count": p_info["word_count"],
            "similarity_score": round(raw_score, 4),
            "similarity_percentage": round(raw_score * 100, 1),
            "matched_terms": matched_terms
        })

    # Sort descending by similarity score
    ranked_candidates.sort(key=lambda x: x["similarity_score"], reverse=True)

    best_match = ranked_candidates[0] if ranked_candidates else None
    top_score = best_match["similarity_score"] if best_match else 0.0
    top_percentage = best_match["similarity_percentage"] if best_match else 0.0

    # Categorize match confidence
    if top_score >= 0.50:
        confidence_label = "High Similarity"
        confidence_color = "green"
    elif top_score >= 0.25:
        confidence_label = "Moderate Similarity"
        confidence_color = "blue"
    elif top_score > 0.05:
        confidence_label = "Low Similarity"
        confidence_color = "amber"
    else:
        confidence_label = "No Direct Match Found"
        confidence_color = "gray"

    return {
        "has_match": top_score > 0.05,
        "best_match": best_match,
        "top_score": top_score,
        "top_percentage": top_percentage,
        "confidence_label": confidence_label,
        "confidence_color": confidence_color,
        "total_paragraphs_compared": len(paragraphs),
        "candidates": ranked_candidates[:top_k],
        "algorithm": "Scikit-Learn TF-IDF + Cosine Metric"
    }


# ==============================================================================
# 2. PROFESSOR'S 128D VECTOR SIMILARITY ENGINE (PRESERVED FROM WORKSPACE)
# ==============================================================================

def generate_professor_embedding(text: str, dim: int = 128) -> List[float]:
    """
    Preserved from the professor's RAG codebase (server.py):
    Generates a deterministic 128-dimensional dense vector with TF-IDF weighting,
    dual hash dispersion (FNV-1a & DJB2), subword 3-grams, and L2 unit norm.
    """
    stopwords = {
        'the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was', 'were',
        'be', 'been', 'being', 'in', 'on', 'at', 'to', 'for', 'with', 'by',
        'about', 'against', 'between', 'into', 'through', 'during', 'before',
        'after', 'above', 'below', 'from', 'up', 'down', 'of', 'off', 'over',
        'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when',
        'where', 'why', 'how', 'all', 'both', 'each', 'few', 'more', 'most',
        'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same',
        'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don',
        'should', 'now', 'what', 'which', 'who', 'this', 'that', 'these', 'those'
    }
    
    vec = [0.0] * dim
    clean_text = text.lower()
    words = re.findall(r'[a-z0-9]+', clean_text)
    
    if not words:
        return [1.0 / math.sqrt(dim)] * dim
        
    for word in words:
        weight = 0.2 if word in stopwords else 1.0 + min(len(word) / 5.0, 1.5)
        
        # Dual hash mixing: FNV-1a & DJB2
        h1 = 2166136261
        for b in word.encode('utf-8'):
            h1 = ((h1 ^ b) * 16777619) & 0xFFFFFFFF
            
        h2 = 5381
        for b in word.encode('utf-8'):
            h2 = (((h2 << 5) + h2) + b) & 0xFFFFFFFF
            
        pos1 = h1 % dim
        pos2 = (h1 >> 16) % dim
        pos3 = h2 % dim
        
        vec[pos1] += weight * 1.0
        vec[pos2] += weight * 0.7
        vec[pos3] += weight * 0.5
        
        # Subword character 3-grams
        if len(word) >= 4:
            for i in range(len(word) - 2):
                tri = word[i:i+3]
                th = 5381
                for b in tri.encode('utf-8'):
                    th = (((th << 5) + th) + b) & 0xFFFFFFFF
                tpos = th % dim
                vec[tpos] += weight * 0.35

    # L2 Unit Normalization: ||v|| = 1.0
    norm = math.sqrt(sum(x * x for x in vec))
    if norm > 0.0:
        vec = [x / norm for x in vec]
    else:
        vec = [1.0 / math.sqrt(dim)] * dim
        
    return vec


def professor_cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Computes exact inner dot product of unit-normalized vectors."""
    dot = sum(a * b for a, b in zip(v1, v2))
    return max(0.0, min(1.0, dot))
