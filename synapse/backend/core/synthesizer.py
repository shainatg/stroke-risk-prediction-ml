"""
Synapse Answer Synthesis & Explainability Engine
================================================
Preserves the grounded answer synthesis algorithm from the original project,
supplemented with rigorous explainability breakdowns that detail exactly why
a specific passage matched the user's query.
"""

import re
from typing import List, Dict, Any

SYNTH_STOP_WORDS = {
    'what', 'when', 'where', 'which', 'who', 'whom', 'whose', 'why', 'how',
    'is', 'are', 'was', 'were', 'the', 'and', 'for', 'with', 'from', 'that',
    'this', 'does', 'differ', 'can', 'you', 'tell', 'about', 'in', 'on', 'at'
}

def synthesize_grounded_answer(query: str, context_chunks: List[Dict[str, Any]], doc_name: str = "Document") -> Dict[str, Any]:
    """
    Synthesizes a factually grounded answer referencing the top retrieved passages.
    Extracts sentences matching salient query terms and formats verifiable citations.
    Preserves core logic from synthesize_educational_answer while providing structured response objects.
    """
    clean_query = (query or '').strip()
    if not context_chunks:
        empty_ans = (
            f'No relevant context passages were retrieved for the query "{clean_query}". '
            'In semantic analysis and RAG, when similarity scores do not meet the relevancy threshold, '
            'the system prevents hallucinations by reporting insufficient grounding information.'
        )
        return {
            "answer_markdown": empty_ans,
            "key_insight": "No matching evidence found in the document.",
            "citations": [],
            "grounded": False
        }

    query_terms = re.sub(r'[^\w\s]', '', clean_query.lower()).split()
    salient_terms = [t for t in query_terms if len(t) > 2 and t not in SYNTH_STOP_WORDS]

    top_chunks = context_chunks[:3]
    matched_sentences = []

    for chunk in top_chunks:
        text = chunk.get("text", "")
        c_idx = chunk.get("index", 0)
        c_score = chunk.get("score", 0.0)
        c_page = chunk.get("page", 1)

        # Split into sentences
        raw_sentences = re.split(r'(?<=[.!?])\s+', text)
        for s in raw_sentences:
            clean_s = s.strip()
            if len(clean_s) < 15:
                continue
            lower_s = clean_s.lower()
            match_count = 0
            for t in salient_terms:
                if t in lower_s:
                    match_count += 2
                elif len(t) > 4 and t[:4] in lower_s:
                    match_count += 1

            if match_count > 0:
                matched_sentences.append({
                    "sentence": clean_s,
                    "score": match_count,
                    "chunkIndex": c_idx,
                    "chunkScore": c_score,
                    "page": c_page
                })

    matched_sentences.sort(key=lambda x: x["score"], reverse=True)

    citations = []
    output_lines = [f'### Grounded Finding for: *"{clean_query}"*\n']

    if matched_sentences:
        top_sentences = matched_sentences[:2]
        output_lines.append("Based directly on the most semantically aligned passage from the uploaded document:\n")
        
        for m in top_sentences:
            cite_str = f'Passage #{m["chunkIndex"] + 1} (Page {m["page"]}) — {m["chunkScore"] * 100:.1f}% Match'
            output_lines.append(f'> "{m["sentence"]}"\n> *— {cite_str}*\n')
            citations.append({
                "passage_index": m["chunkIndex"] + 1,
                "page": m["page"],
                "similarity_score": round(m["chunkScore"], 4),
                "similarity_pct": f"{m['chunkScore'] * 100:.1f}%",
                "quote": m["sentence"]
            })
            
        key_insight = " ".join(m["sentence"] for m in top_sentences)
        output_lines.append(f'\n**Primary Synthesis:** {key_insight}')
    else:
        top_chunk = top_chunks[0]
        c_idx = top_chunk.get("index", 0) + 1
        c_page = top_chunk.get("page", 1)
        c_score = top_chunk.get("score", 0.0)
        c_text = top_chunk.get("text", "")[:320]
        
        output_lines.append(f'Based on the highest matching retrieved context (Passage #{c_idx}, Page {c_page}, {c_score * 100:.1f}% match):\n')
        output_lines.append(f'> "{c_text}..."\n')
        key_insight = c_text
        citations.append({
            "passage_index": c_idx,
            "page": c_page,
            "similarity_score": round(c_score, 4),
            "similarity_pct": f"{c_score * 100:.1f}%",
            "quote": c_text
        })

    return {
        "answer_markdown": "\n".join(output_lines),
        "key_insight": key_insight,
        "citations": citations,
        "grounded": True
    }


def synthesize_normal_llm_answer(query: str) -> str:
    """
    Simulates standard ungrounded LLM generation based purely on pre-trained memory.
    Demonstrates lack of access to private/uploaded data and lack of source citations.
    Preserved exactly from the original server.py implementation.
    """
    clean = (query or '').lower()

    if any(k in clean for k in ['apex', 'sec-2026', 'burner', 'category-a', 'policy', 'travel', 'vpn', 'mfa']):
        return (
            "As a standard AI language model relying solely on pre-trained memory, I do not have access "
            "to your organization's internal employee handbook, private document SEC-2026-v4, or confidential travel security protocols.\n\n"
            "In general, enterprise cybersecurity guidelines suggest using a corporate VPN and contacting your IT team prior to departure. "
            "However, I cannot verify specific requirements, notice periods (e.g. 7 business days), or hardware restrictions "
            "(such as 'traveler burner laptops') without the relevant documentation.\n\n"
            "⚠️ Limitation: Pure LLM lacks private proprietary documents and cannot provide company-specific answers."
        )

    if any(k in clean for k in ['moxie', 'mars', 'perseverance', 'ingenuity']):
        return (
            "MOXIE (Mars Oxygen ISRU Experiment) is an instrument aboard NASA's Perseverance rover intended to "
            "demonstrate producing oxygen from the Martian atmospheric carbon dioxide.\n\n"
            "While it successfully ran tests converting carbon dioxide into breathable oxygen during the mission, my base training "
            "does not track the exact total grams produced across all runs or specific operational milestones without live retrieval.\n\n"
            "⚠️ Limitation: Pure LLM relies on general pre-training and may omit exact experimental metrics or latest mission updates."
        )

    if any(k in clean for k in ['quantum', 'qubit', 'superposition', 'entanglement', 'refrigerator', 'shor']):
        return (
            "Quantum computing utilizes principles of quantum mechanics such as superposition and entanglement to perform complex computations. "
            "Qubits can represent combinations of 0 and 1 simultaneously, unlike classical binary bits. To maintain coherence, quantum chips are "
            "typically housed in cryogenic dilution refrigerators cooled near absolute zero.\n\n"
            "⚠️ Limitation: Pure LLM gives a general textbook summary, but cannot quote or cite the specific passages, page numbers, "
            "or exact phrasing from your uploaded reference document."
        )

    return (
        f'Based purely on pre-trained parametric knowledge: Answering "{query}". '
        'A standard language model generates text token-by-token based on generic training patterns, '
        'without verifiable grounding, passage citations, or page numbers from your uploaded document.\n\n'
        '⚠️ Limitation: Pure LLM generation cannot cite sources, lacks private document context, and cannot guarantee grounding in your selected file.'
    )


def explain_similarity_match(
    query: str, 
    chunk: Dict[str, Any], 
    score: float,
    query_vector: List[float],
    chunk_vector: List[float]
) -> Dict[str, Any]:
    """
    Produces a detailed, transparent explainability card detailing why the passage matched.
    """
    q_words = set(re.findall(r'\b\w{3,}\b', (query or '').lower())) - SYNTH_STOP_WORDS
    c_words = set(re.findall(r'\b\w{3,}\b', chunk.get("text", "").lower()))
    
    exact_matches = sorted(list(q_words & c_words))
    stem_matches = []
    for qw in q_words:
        if qw not in exact_matches:
            for cw in c_words:
                if len(qw) >= 4 and len(cw) >= 4 and (qw[:4] == cw[:4]):
                    stem_matches.append(f"{qw} ~ {cw}")
                    break

    # Vector dot product components
    dot_product = sum(a * b for a, b in zip(query_vector, chunk_vector))
    
    # Calculate top contributing dimensions (highest positive product a_i * b_i)
    dimension_contributions = []
    for d, (a, b) in enumerate(zip(query_vector, chunk_vector)):
        dimension_contributions.append((d, a * b))
    dimension_contributions.sort(key=lambda x: x[1], reverse=True)
    top_dims = dimension_contributions[:5]

    explanation_text = (
        f"This passage achieved a cosine similarity score of {score:.4f} ({score * 100:.1f}% match). "
        f"The 128D semantic hash vectors exhibited strong alignment across dimensions "
        f"({', '.join(f'D{d}:{v:+.3f}' for d, v in top_dims)}). "
    )
    if exact_matches:
        explanation_text += f"Key semantic terms directly co-occurring include: {', '.join(exact_matches)}."
    elif stem_matches:
        explanation_text += f"Morphological subword overlaps include: {', '.join(stem_matches)}."
    else:
        explanation_text += "Subword 3-gram character hashes and semantic topic locality drove the match."

    return {
        "similarity_score": round(score, 4),
        "similarity_percentage": round(score * 100, 2),
        "exact_term_matches": exact_matches,
        "stem_matches": stem_matches,
        "dot_product": round(dot_product, 6),
        "top_contributing_dimensions": [{"dimension": d, "contribution": round(c, 4)} for d, c in top_dims],
        "explanation": explanation_text
    }
