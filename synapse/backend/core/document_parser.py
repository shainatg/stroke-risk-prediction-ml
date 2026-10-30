"""
Synapse Document Parser
=======================
Robust multi-format document parser supporting PDF, DOCX, TXT, and CSV.
Extracts structured text with page boundaries, character offsets,
and metadata for downstream passage citation and document viewing.
"""

import os
import csv
import io
from pathlib import Path
from typing import Dict, Any, List, Tuple

try:
    import pypdf
except ImportError:
    pypdf = None

try:
    import docx
except ImportError:
    docx = None


class DocumentParser:
    """Parses uploaded files into unified text representations with page/section tracking."""

    @staticmethod
    def parse_file(file_path: Path, filename: str) -> Dict[str, Any]:
        ext = filename.lower().split('.')[-1]
        
        if ext == "pdf":
            return DocumentParser._parse_pdf(file_path, filename)
        elif ext in ("docx", "doc"):
            return DocumentParser._parse_docx(file_path, filename)
        elif ext == "csv":
            return DocumentParser._parse_csv(file_path, filename)
        elif ext in ("txt", "md", "text"):
            return DocumentParser._parse_txt(file_path, filename)
        else:
            raise ValueError(f"Unsupported file format: '.{ext}'. Supported formats: PDF, DOCX, TXT, CSV.")

    @staticmethod
    def _parse_pdf(file_path: Path, filename: str) -> Dict[str, Any]:
        if pypdf is None:
            raise RuntimeError("pypdf library is not installed.")

        reader = pypdf.PdfReader(str(file_path))
        num_pages = len(reader.pages)
        if num_pages == 0:
            raise ValueError("The uploaded PDF has 0 pages or is empty.")

        pages_data = []
        full_text_parts = []
        current_char = 0

        for i, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            page_text = page_text.strip()
            start_c = current_char
            end_c = current_char + len(page_text)
            
            pages_data.append({
                "page": i + 1,
                "text": page_text,
                "start_char": start_c,
                "end_char": end_c,
                "char_count": len(page_text),
                "word_count": len(page_text.split())
            })
            
            full_text_parts.append(page_text)
            current_char = end_c + 2  # account for newline separator

        full_text = "\n\n".join(full_text_parts).strip()
        if not full_text:
            raise ValueError("Could not extract any readable text from this PDF. It may contain scanned images without OCR.")

        return {
            "filename": filename,
            "file_type": "pdf",
            "file_size": file_path.stat().st_size,
            "total_pages": num_pages,
            "full_text": full_text,
            "pages": pages_data,
            "word_count": len(full_text.split()),
            "char_count": len(full_text)
        }

    @staticmethod
    def _parse_docx(file_path: Path, filename: str) -> Dict[str, Any]:
        if docx is None:
            raise RuntimeError("python-docx library is not installed.")

        doc = docx.Document(str(file_path))
        paragraphs = []
        
        for p in doc.paragraphs:
            text = p.text.strip()
            if text:
                paragraphs.append(text)

        # Also extract table text
        for table in doc.tables:
            for row in table.rows:
                row_cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_cells:
                    paragraphs.append(" | ".join(row_cells))

        full_text = "\n\n".join(paragraphs).strip()
        if not full_text:
            raise ValueError("The uploaded DOCX document contains no readable text.")

        # Estimate pages based on word counts (~350 words per page)
        words = full_text.split()
        words_per_page = 350
        est_pages = max(1, (len(words) + words_per_page - 1) // words_per_page)
        
        pages_data = []
        char_idx = 0
        for p_idx in range(est_pages):
            w_slice = words[p_idx * words_per_page : (p_idx + 1) * words_per_page]
            p_text = " ".join(w_slice)
            pages_data.append({
                "page": p_idx + 1,
                "text": p_text,
                "start_char": char_idx,
                "end_char": char_idx + len(p_text),
                "char_count": len(p_text),
                "word_count": len(w_slice)
            })
            char_idx += len(p_text) + 1

        return {
            "filename": filename,
            "file_type": "docx",
            "file_size": file_path.stat().st_size,
            "total_pages": est_pages,
            "full_text": full_text,
            "pages": pages_data,
            "word_count": len(words),
            "char_count": len(full_text)
        }

    @staticmethod
    def _parse_txt(file_path: Path, filename: str) -> Dict[str, Any]:
        content = None
        for encoding in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
            try:
                with open(file_path, "r", encoding=encoding) as f:
                    content = f.read()
                break
            except UnicodeDecodeError:
                continue

        if content is None:
            raise ValueError("Could not decode text file with UTF-8 or standard encodings.")

        content = content.strip()
        if not content:
            raise ValueError("The uploaded text file is empty.")

        words = content.split()
        words_per_page = 350
        est_pages = max(1, (len(words) + words_per_page - 1) // words_per_page)
        
        pages_data = []
        char_idx = 0
        for p_idx in range(est_pages):
            w_slice = words[p_idx * words_per_page : (p_idx + 1) * words_per_page]
            p_text = " ".join(w_slice)
            pages_data.append({
                "page": p_idx + 1,
                "text": p_text,
                "start_char": char_idx,
                "end_char": char_idx + len(p_text),
                "char_count": len(p_text),
                "word_count": len(w_slice)
            })
            char_idx += len(p_text) + 1

        return {
            "filename": filename,
            "file_type": "txt",
            "file_size": file_path.stat().st_size,
            "total_pages": est_pages,
            "full_text": content,
            "pages": pages_data,
            "word_count": len(words),
            "char_count": len(content)
        }

    @staticmethod
    def _parse_csv(file_path: Path, filename: str) -> Dict[str, Any]:
        lines = []
        raw_rows = []
        for encoding in ("utf-8", "utf-8-sig", "latin-1"):
            try:
                with open(file_path, "r", encoding=encoding, newline="") as f:
                    reader = csv.reader(f)
                    header = None
                    for row_idx, row in enumerate(reader):
                        if not row:
                            continue
                        if header is None:
                            header = [h.strip() for h in row]
                            lines.append(f"Columns: {', '.join(header)}")
                        else:
                            raw_rows.append(row)
                            # Create semantically rich row representation
                            row_desc = []
                            for h, val in zip(header, row):
                                if val.strip():
                                    row_desc.append(f"{h}: {val.strip()}")
                            lines.append(f"Row {row_idx} -> " + " | ".join(row_desc))
                break
            except UnicodeDecodeError:
                continue

        if not lines:
            raise ValueError("The uploaded CSV file is empty or could not be parsed.")

        full_text = "\n".join(lines)
        words = full_text.split()
        rows_per_page = 25
        est_pages = max(1, (len(raw_rows) + rows_per_page - 1) // rows_per_page) if raw_rows else 1

        pages_data = []
        char_idx = 0
        for p_idx in range(est_pages):
            start_r = p_idx * rows_per_page
            end_r = (p_idx + 1) * rows_per_page
            p_slice = lines[start_r:end_r]
            p_text = "\n".join(p_slice)
            pages_data.append({
                "page": p_idx + 1,
                "text": p_text,
                "start_char": char_idx,
                "end_char": char_idx + len(p_text),
                "char_count": len(p_text),
                "word_count": len(p_text.split())
            })
            char_idx += len(p_text) + 1

        return {
            "filename": filename,
            "file_type": "csv",
            "file_size": file_path.stat().st_size,
            "total_pages": est_pages,
            "full_text": full_text,
            "pages": pages_data,
            "word_count": len(words),
            "char_count": len(full_text),
            "csv_rows": len(raw_rows)
        }
