#!/usr/bin/env python3
"""
DOCX -> guidelines.index.json

Parses a .docx version of the Federal Plain Language Guidelines into
chunked JSON for the web app at apps/plain-check-web/public/data/guidelines.index.json.

- Preserves heading hierarchy (Heading 1/2/3…)
- Chunks by character budget with small overlap for better retrieval
- Adds section metadata so the UI can show where a suggestion came from

Usage (PowerShell):
  python scripts/docx_to_guidelines_index.py `
    --docx "C:\path\to\FederalPLGuidelines.docx" `
    --out "apps\plain-check-web\public\data\guidelines.index.json"

Dependencies:
  pip install python-docx
"""

import argparse
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    from docx import Document
except ImportError as e:
    raise SystemExit("Missing dependency: python-docx. Install with:\n  pip install python-docx")

# -------- Helpers --------

HEADING_RE = re.compile(r"^Heading\s+(\d+)$", re.IGNORECASE)

def para_text(p) -> str:
    # Join runs; keep inline text only
    t = p.text or ""
    # Normalize whitespace
    t = re.sub(r"\s+", " ", t).strip()
    return t

def get_heading_level(p) -> Optional[int]:
    """Return 1..9 for 'Heading 1..9', else None."""
    try:
        style = p.style
        name = getattr(style, "name", "") or ""
        m = HEADING_RE.match(name.strip())
        if m:
            return int(m.group(1))
    except Exception:
        pass
    return None

def build_blocks(doc: Document) -> List[Dict[str, Any]]:
    """
    Convert the DOCX into a sequence of blocks:
      {'type': 'heading'|'para'|'bullet'|'numbered', 'level': int|None, 'text': str}
    """
    blocks = []
    for p in doc.paragraphs:
        text = para_text(p)
        if not text:
            continue

        lvl = get_heading_level(p)
        if lvl:
            blocks.append({"type": "heading", "level": lvl, "text": text})
            continue

        # very light list detection (based on numbering/bullet style name)
        style_name = (getattr(getattr(p, "style", None), "name", "") or "").lower()
        if "bullet" in style_name:
            blocks.append({"type": "bullet", "level": None, "text": text})
        elif "number" in style_name or "list" in style_name:
            blocks.append({"type": "numbered", "level": None, "text": text})
        else:
            blocks.append({"type": "para", "level": None, "text": text})
    return blocks

def join_section_path(path: List[str]) -> str:
    return " / ".join([x for x in path if x])

def chunk_section_text(section_text: str, max_chars=1200, overlap=120) -> List[str]:
    """
    Chunk a section's text by character budget with a little character overlap.
    Split preference: paragraph boundaries (double newline) if present.
    """
    paras = [p for p in section_text.split("\n\n") if p.strip()]
    chunks = []
    cur: List[str] = []
    for p in paras:
        joined = ("\n\n".join(cur)).strip()
        if not joined:
            cur = [p]
            continue
        if len(joined) + 2 + len(p) <= max_chars:
            cur.append(p)
        else:
            if joined:
                chunks.append(joined)
            # start new with overlap from the tail of previous text
            tail = joined[-overlap:] if overlap > 0 else ""
            cur = [tail, p] if tail else [p]
    if cur:
        joined = ("\n\n".join(cur)).strip()
        if joined:
            chunks.append(joined)
    return chunks

def build_sections(blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Turn flat blocks into sections keyed by the heading path.
    Each section accumulates text until the next heading of same or higher level.
    """
    sections: List[Dict[str, Any]] = []
    heading_stack: List[str] = []
    buf: List[str] = []

    def flush():
        nonlocal buf
        if not buf:
            return
        text = "\n\n".join(buf).strip()
        if text:
            sections.append({
                "path": heading_stack.copy(),
                "text": text
            })
        buf = []

    for b in blocks:
        if b["type"] == "heading":
            # starting a new heading: first flush previous buffer
            flush()
            lvl = b["level"]
            # shrink/extend stack
            if len(heading_stack) >= lvl:
                heading_stack = heading_stack[:lvl-1]
            # push this heading
            heading_stack.append(b["text"])
        else:
            buf.append(b["text"])

    flush()
    return sections

# -------- Main pipeline --------

def docx_to_index(docx_path: Path, out_path: Path, max_chars: int, overlap: int) -> Dict[str, Any]:
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        raise SystemExit("Missing dependency: sentence-transformers. Install with:\n  pip install sentence-transformers")
    
    model = SentenceTransformer('all-MiniLM-L6-v2')

    doc = Document(str(docx_path))
    blocks = build_blocks(doc)
    sections = build_sections(blocks)

    # Build chunks with metadata
    chunks_out: List[Dict[str, Any]] = []
    for sec_idx, sec in enumerate(sections):
        sec_text = sec["text"]
        sec_path = sec["path"]
        sec_title = sec_path[-1] if sec_path else ""
        chunk_texts = chunk_section_text(sec_text, max_chars=max_chars, overlap=overlap)
        for j, ctext in enumerate(chunk_texts):
            chunks_out.append({
                "id": f"sec{sec_idx:04d}-chunk{j:02d}",
                "text": ctext,
                "section_path": sec_path,
                "heading": sec_title,
                "heading_full": join_section_path(sec_path),
                "char_start": None,
                "char_end": None,
                "page_start": None,   # pages not derivable from DOCX reliably
                "page_end": None,
                "embedding": model.encode(ctext).tolist()
            })

    index = {
        "source": "Federal Plain Language Guidelines (DOCX)",
        "docx_filename": docx_path.name,
        "num_sections": len(sections),
        "num_chunks": len(chunks_out),
        "chunker": {"max_chars": max_chars, "overlap": overlap, "by": "heading/paragraph"},
        "chunks": chunks_out
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    # Default utf-8 is already no BOM
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    return index


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--docx", type=Path, required=True, help="Path to FederalPLGuidelines.docx")
    ap.add_argument("--out", type=Path, required=True, help="Where to write guidelines.index.json")
    ap.add_argument("--max-chars", type=int, default=1200)
    ap.add_argument("--overlap", type=int, default=120)
    args = ap.parse_args()

    idx = docx_to_index(args.docx, args.out, args.max_chars, args.overlap)
    print(f"Wrote {args.out} with {idx['num_chunks']} chunks from {idx['num_sections']} sections.")

if __name__ == "__main__":
    main()
