"""
Synapse Local Database Layer
============================
SQLite persistence engine for documents, parsed chunks, and semantic analysis histories.
Provides search, audit tracking, and instant reload capabilities.
"""

import sqlite3
import json
import uuid
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "synapse.db"

def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id TEXT PRIMARY KEY,
        filename TEXT NOT NULL,
        file_type TEXT NOT NULL,
        file_size INTEGER NOT NULL,
        char_count INTEGER NOT NULL,
        word_count INTEGER NOT NULL,
        chunk_count INTEGER NOT NULL,
        total_pages INTEGER NOT NULL,
        full_text TEXT NOT NULL,
        pages_json TEXT NOT NULL,
        chunks_json TEXT NOT NULL,
        created_at REAL NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analyses (
        id TEXT PRIMARY KEY,
        document_id TEXT NOT NULL,
        document_name TEXT NOT NULL,
        query TEXT NOT NULL,
        answer_markdown TEXT NOT NULL,
        key_insight TEXT NOT NULL,
        top_score REAL NOT NULL,
        top_chunk_index INTEGER NOT NULL,
        top_page INTEGER NOT NULL,
        top_passage_text TEXT NOT NULL,
        duration_ms REAL NOT NULL,
        full_result_json TEXT NOT NULL,
        created_at REAL NOT NULL,
        FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
    )
    """)

    conn.commit()
    conn.close()


def save_document(doc_data: Dict[str, Any], chunks: List[Dict[str, Any]]) -> str:
    doc_id = str(uuid.uuid4())
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO documents (
        id, filename, file_type, file_size, char_count, word_count, 
        chunk_count, total_pages, full_text, pages_json, chunks_json, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        doc_id,
        doc_data["filename"],
        doc_data["file_type"],
        doc_data["file_size"],
        doc_data["char_count"],
        doc_data["word_count"],
        len(chunks),
        doc_data.get("total_pages", 1),
        doc_data["full_text"],
        json.dumps(doc_data.get("pages", [])),
        json.dumps(chunks),
        time.time()
    ))

    conn.commit()
    conn.close()
    return doc_id


def list_documents() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, filename, file_type, file_size, char_count, word_count, 
           chunk_count, total_pages, created_at
    FROM documents 
    ORDER BY created_at DESC
    """)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def get_document(doc_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    d["pages"] = json.loads(d["pages_json"])
    d["chunks"] = json.loads(d["chunks_json"])
    return d


def delete_document(doc_id: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
    cursor.execute("DELETE FROM analyses WHERE document_id = ?", (doc_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted


def save_analysis(
    doc_id: str,
    doc_name: str,
    query: str,
    answer_markdown: str,
    key_insight: str,
    top_score: float,
    top_chunk_idx: int,
    top_page: int,
    top_text: str,
    duration_ms: float,
    full_result: Dict[str, Any]
) -> str:
    analysis_id = str(uuid.uuid4())
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO analyses (
        id, document_id, document_name, query, answer_markdown, key_insight,
        top_score, top_chunk_index, top_page, top_passage_text, duration_ms,
        full_result_json, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        analysis_id,
        doc_id,
        doc_name,
        query,
        answer_markdown,
        key_insight,
        top_score,
        top_chunk_idx,
        top_page,
        top_text,
        duration_ms,
        json.dumps(full_result),
        time.time()
    ))

    conn.commit()
    conn.close()
    return analysis_id


def list_analyses(search: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    if search:
        s = f"%{search}%"
        cursor.execute("""
        SELECT id, document_id, document_name, query, key_insight, top_score, 
               top_chunk_index, top_page, top_passage_text, duration_ms, created_at
        FROM analyses
        WHERE query LIKE ? OR document_name LIKE ? OR key_insight LIKE ?
        ORDER BY created_at DESC
        LIMIT 50
        """, (s, s, s))
    else:
        cursor.execute("""
        SELECT id, document_id, document_name, query, key_insight, top_score, 
               top_chunk_index, top_page, top_passage_text, duration_ms, created_at
        FROM analyses
        ORDER BY created_at DESC
        LIMIT 50
        """)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def get_analysis(analysis_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM analyses WHERE id = ?", (analysis_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    d["full_result"] = json.loads(d["full_result_json"])
    return d


def delete_analysis(analysis_id: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM analyses WHERE id = ?", (analysis_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted
