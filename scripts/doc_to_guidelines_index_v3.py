#!/usr/bin/env python3
"""
DOCX -> guidelines.json.index (regions + outline; retrieval = body only)

What this script does:
- Identifies document regions: title_page, introduction, revision_note, toc, body
- Keeps title/revision/TOC as metadata/sections (retrievable: false)
- Builds an explicit outline (H1–H3) for the body and links sections/chunks to outline nodes
- Sentence-aware chunking with context-only overlap for body sections only
- Emits a per-role quality report

Usage (PowerShell):
  python scripts\docx_to_guidelines_index_regions.py ^
    --docx "C:\Development\plain-language\FederalPLGuidelines.docx" ^
    --out  "apps\plain-check-web\public\data\guidelines.json.index" ^
    --target-chars 1100 --min-chars 700 --overlap 120 --max-heading-level 3
"""

import argparse, json, re, datetime, hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

try:
    from docx import Document
except ImportError:
    raise SystemExit("Missing dependency: python-docx. Install with: python -m pip install python-docx")

# --------- Config defaults ----------
DEFAULT_TARGET = 1100
DEFAULT_MIN    = 700
DEFAULT_OVERLAP= 120
DEFAULT_MAXLVL = 3
MIN_SECTION_FOR_MERGE = 400   # sections below this char count may be merged with a sibling

# --------- Regexes ----------
HEADING_STYLE_RE = re.compile(r"^Heading\s+(\d+)$", re.IGNORECASE)

ROMAN_RE   = r"(?:M{0,4}(?:CM|CD|D?C{0,3}))?(?:XC|XL|L?X{0,3})?(?:IX|IV|V?I{0,3})"
IS_ROMAN   = re.compile(rf"^\s*({ROMAN_RE})\.\s+\S")
IS_NUM     = re.compile(r"^\s*\d+(\.\d+)*\.\s+\S")   # 1., 1.2., 1.2.3.
IS_ALPHA   = re.compile(r"^\s*[A-Za-z]\.\s+\S")     # a. b. ...
ALL_CAPS   = re.compile(r"^[A-Z0-9\s\-–—:&/]{6,}$")
TOC_TITLE  = re.compile(r"^\s*Table of Contents\s*$", re.IGNORECASE)
REVISION_H = re.compile(r"^\s*Revision\b", re.IGNORECASE)
INTRO_H    = re.compile(r"^\s*Introduction\s*$", re.IGNORECASE)

# Remove trailing dot leaders + page numbers, e.g. "…..... 17"
TRAILING_PAGES = re.compile(r"\s[.\s•·]*\d{1,4}\s*$")

# Lightweight sentence splitter
SENT_SPLIT = re.compile(r"(?<=[\.\?!])\s+(?=[A-Z0-9“\"'])")

def now_iso() -> str:
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def norm_space(s: str) -> str:
    s = (s or "").replace("\u00AD","")            # soft hyphen
    s = s.replace("—", "-").replace("–","-")      # normalize dashes
    s = re.sub(r"\s+", " ", s)
    return s.strip()

def clean_heading(h: str) -> str:
    h = norm_space(h)
    h = TRAILING_PAGES.sub("", h)  # strip trailing page numbers/leaders
    return h.strip()

def para_text(p) -> str:
    return norm_space(p.text)

def get_heading_level_from_style(p) -> Optional[int]:
    try:
        name = (getattr(p.style, "name", "") or "").strip()
        m = HEADING_STYLE_RE.match(name)
        if m:
            return int(m.group(1))
    except Exception:
        pass
    return None

def guess_heading_level_from_text(text: str) -> Optional[int]:
    if IS_ROMAN.match(text): return 1
    if ALL_CAPS.match(text): return 1
    if IS_NUM.match(text):   return 2
    if IS_ALPHA.match(text): return 3
    return None

def is_toc_para(p, t: str) -> bool:
    name = (getattr(p.style, "name", "") or "")
    if name.startswith("TOC ") or name == "TOC Heading":
        return True
    # lines with dot leaders and trailing page numbers
    if TRAILING_PAGES.search(t):
        return True
    return False

# --------- Block reading with region detection ----------
def read_blocks_with_roles(doc: Document) -> List[Dict[str, Any]]:
    """
    Walk paragraphs and emit blocks:
      {"type": "heading"|"para", "level": int|None, "text": str, "role": str}

    Region state machine based on the typical order:
      title_page (pre H1) -> introduction (H1 "Introduction") -> revision_note (H1 "Revision...")
      -> toc (H1 "Table of Contents" or TOC styles) -> body (remaining)
    """
    raw = []
    for p in doc.paragraphs:
        t = para_text(p)
        if not t:
            continue
        raw.append((p, t))

    role = "title_page"
    in_toc = False
    toc_streak = 0
    blocks: List[Dict[str, Any]] = []

    for p, t in raw:
        lvl = get_heading_level_from_style(p)
        hl = lvl if lvl is not None else guess_heading_level_from_text(t)
        ht = clean_heading(t) if (lvl or hl) else t

        # TOC detection & transitions
        if role != "toc":
            if TOC_TITLE.match(ht) or is_toc_para(p, t):
                role = "toc"
                in_toc = True
                toc_streak = 0

        if role == "toc":
            # Stay in toc while paragraphs look like TOC or until next H1 that isn't TOC
            if is_toc_para(p, t):
                toc_streak = 0
                # We still record the TOC as blocks (so it can be captured in a section), but not retrievable later
                if hl:
                    blocks.append({"type":"heading","level":int(hl), "text": clean_heading(t), "role": role})
                else:
                    blocks.append({"type":"para",   "level":None,     "text": t,               "role": role})
                continue
            toc_streak += 1
            # Escape TOC after a short run of non-TOC paras or a clear H1
            if hl == 1 or toc_streak >= 3:
                role = "body"
                in_toc = False
            else:
                # still in toc with stray para
                blocks.append({"type":"para","level":None,"text":t,"role":role})
                continue

        # Handle role transitions outside TOC
        if role == "title_page" and hl == 1:
            # Heading 1 encountered — decide if it's Intro/Revision/TOC or start of body
            if INTRO_H.match(ht):
                role = "introduction"
            elif REVISION_H.match(ht):
                role = "revision_note"
            elif TOC_TITLE.match(ht):
                role = "toc"; in_toc = True; toc_streak = 0
            else:
                role = "body"

        elif role in ("introduction", "revision_note"):
            # If another H1 appears, switch depending on its title
            if hl == 1 and not INTRO_H.match(ht) and not REVISION_H.match(ht):
                if TOC_TITLE.match(ht):
                    role = "toc"; in_toc = True; toc_streak = 0
                else:
                    role = "body"

        # Record block with current role
        if hl:
            blocks.append({"type":"heading","level":int(hl),"text": clean_heading(t),"role":role})
        else:
            blocks.append({"type":"para","level":None,"text":t,"role":role})

    return blocks

# --------- Outline (body only) ----------
def build_outline(blocks: List[Dict[str, Any]], max_heading_level: int) -> Tuple[List[Dict[str, Any]], Dict[Tuple[str, ...], str]]:
    """
    Returns:
      - outline: list of nodes {id, level, title, parent}
      - path_to_outline_id: map from body heading path to outline_id
    Only headings in role == 'body' are considered.
    """
    outline: List[Dict[str, Any]] = []
    path: List[str] = []
    id_counters = {1:0, 2:0, 3:0}
    path_to_outline_id: Dict[Tuple[str, ...], str] = {}

    def new_id(level: int) -> str:
        id_counters[level] += 1
        return f"h{level}-{id_counters[level]:03d}"

    for b in blocks:
        if b["type"] != "heading" or b["role"] != "body":
            continue
        lvl = max(1, min(9, int(b["level"])))
        lvl = min(lvl, max_heading_level)
        # adjust path
        if len(path) >= lvl:
            path[:] = path[:lvl-1]
        path.append(b["text"])

        if lvl <= 3:
            oid = new_id(lvl)
            parent = None
            if lvl > 1:
                # parent is the nearest higher-level node in outline (track by last seen)
                # Find the last outline node with level < current
                for prev in reversed(outline):
                    if prev["level"] < lvl:
                        parent = prev["id"]
                        break
            outline.append({"id": oid, "level": lvl, "title": b["text"], "parent": parent})
            path_to_outline_id[tuple(path)] = oid
        else:
            # deeper than 3 — we still need to track path for section mapping
            path_to_outline_id[tuple(path)] = None

    return outline, path_to_outline_id

# --------- Sections ----------
def build_sections(blocks: List[Dict[str, Any]], max_heading_level: int,
                   path_to_outline_id: Dict[Tuple[str, ...], str]) -> List[Dict[str, Any]]:
    """Group paragraphs under a capped heading path, carrying role and outline_id."""
    sections: List[Dict[str, Any]] = []
    path: List[str] = []
    role: Optional[str] = None
    buf: List[str] = []
    sec_counter = 0

    def retrievable_for_role(r: str) -> bool:
        return r == "body"  # only body is retrievable/chunked

    def flush(curr_path: List[str], curr_role: Optional[str]):
        nonlocal buf, sec_counter
        if not buf:
            return
        text = "\n\n".join([b for b in buf if b.strip()]).strip()
        buf = []
        if not text:
            return
        title = curr_path[-1] if curr_path else ""
        outline_id = path_to_outline_id.get(tuple(curr_path))
        sections.append({
            "id": f"sec{sec_counter:04d}",
            "path": curr_path.copy(),
            "title": title,
            "text": text,
            "role": curr_role or "unknown",
            "outline_id": outline_id,
            "retrievable": retrievable_for_role(curr_role or "unknown")
        })
        sec_counter += 1

    for b in blocks:
        if b["type"] == "heading":
            # flush under the *current* path/role BEFORE changing it
            flush(path, role)
            role = b["role"]
            lvl = max(1, min(9, int(b["level"])))
            capped = min(lvl, max_heading_level)
            if len(path) >= capped:
                path[:] = path[:capped-1]
            path.append(b["text"])
        else:
            # para
            if role is None:
                role = b["role"]
            buf.append(b["text"])
    flush(path, role)

    # Merge tiny sections into nearest previous sibling with same parent & role
    merged: List[Dict[str, Any]] = []
    for s in sections:
        parent = (tuple(s["path"][:-1]), s["role"])
        if s["retrievable"] and len(s["text"]) < MIN_SECTION_FOR_MERGE:
            if merged:
                prev = merged[-1]
                prev_parent = (tuple(prev["path"][:-1]), prev["role"])
                if prev["retrievable"] and prev_parent == parent:
                    prev["text"] = (prev["text"].rstrip() + "\n\n" + s["text"].lstrip()).strip()
                    continue  # skip adding s
        merged.append(s)

    # Reassign ids after merges
    for i, s in enumerate(merged):
        s["id"] = f"sec{i:04d}"

    return merged

# --------- Chunking (body only) ----------
def split_sentences(text: str) -> List[str]:
    s = text.strip()
    if not s:
        return []
    parts = SENT_SPLIT.split(s)
    merged: List[str] = []
    cur = ""
    for part in parts:
        if not cur:
            cur = part
            continue
        if len(cur) < 60 and len(cur) + 1 + len(part) <= 140:
            cur = f"{cur} {part}"
        else:
            merged.append(cur.strip())
            cur = part
    if cur:
        merged.append(cur.strip())
    return merged

def make_chunks(section: Dict[str, Any], target_chars=DEFAULT_TARGET, min_chars=DEFAULT_MIN, overlap=DEFAULT_OVERLAP) -> List[Dict[str, Any]]:
    if not section.get("retrievable", True):
        return []
    sents = split_sentences(section["text"])
    chunks: List[Dict[str, Any]] = []
    cur: List[str] = []
    last_tail = ""  # previous chunk's tail

    def push(text: str, ctx_before: str):
        chunks.append({
            "id": f"{section['id']}-ch{len(chunks):02d}",
            "section_id": section["id"],
            "section_path": section["path"],
            "heading": section["title"],
            "heading_full": " / ".join(section["path"]),
            "outline_id": section.get("outline_id"),
            "role": section.get("role"),
            "text": text,
            "context_before": ctx_before,  # context from previous chunk only
            "char_count": len(text),
            "page_start": None,
            "page_end": None,
            "embedding": None
        })

    for s in sents:
        joined = "\n\n".join(cur).strip()
        if not joined:
            cur = [s]
            continue
        if len(joined) + 2 + len(s) <= target_chars:
            cur.append(s)
        else:
            text = joined
            if len(text) < min_chars and chunks:
                prev = chunks.pop()
                merged = (prev["text"] + "\n\n" + text).strip()
                prev["text"] = merged
                prev["char_count"] = len(merged)
                last_tail = merged[-overlap:] if overlap > 0 else ""
                chunks.append(prev)
            else:
                push(text, last_tail)
                last_tail = text[-overlap:] if overlap > 0 else ""
            cur = [s]

    if cur:
        text = "\n\n".join(cur).strip()
        if len(text) < min_chars and chunks:
            prev = chunks.pop()
            merged = (prev["text"] + "\n\n" + text).strip()
            prev["text"] = merged
            prev["char_count"] = len(merged)
            last_tail = merged[-overlap:] if overlap > 0 else ""
            chunks.append(prev)
        else:
            push(text, last_tail)

    return chunks

# --------- Build index ----------
def build(docx: Path, out_path: Path, target_chars: int, min_chars: int, overlap: int, max_heading_level: int) -> Dict[str, Any]:
    doc = Document(str(docx))
    blocks = read_blocks_with_roles(doc)

    # Outline (body only) and mapping path->outline_id
    outline, path_to_outline_id = build_outline(blocks, max_heading_level=max_heading_level)

    # Sections (all roles)
    sections = build_sections(blocks, max_heading_level=max_heading_level, path_to_outline_id=path_to_outline_id)

    # Chunks (body only, because retrievable is based on role)
    chunks: List[Dict[str, Any]] = []
    for s in sections:
        chunks.extend(make_chunks(s, target_chars=target_chars, min_chars=min_chars, overlap=overlap))

    # Meta (best-effort parse from title_page & revision_note)
    meta_title = None
    meta_edition = None
    meta_revision = None

    # Collect front-matter text by role
    role_texts: Dict[str, List[str]] = {"title_page": [], "introduction": [], "revision_note": [], "toc": []}
    for b in blocks:
        if b["role"] in role_texts:
            if b["type"] == "heading":
                role_texts[b["role"]].append(b["text"])
            else:
                role_texts[b["role"]].append(b["text"])

    title_blob = " ".join(role_texts["title_page"]).strip()
    rev_blob   = " ".join(role_texts["revision_note"]).strip()

    # Heuristic extraction
    if title_blob:
        # First reasonably long capitalized line often the doc title
        m = re.search(r"(Federal Plain Language Guidelines)", title_blob, re.IGNORECASE)
        if m:
            meta_title = m.group(1)
        m2 = re.search(r"(March\s+\d{4})", title_blob)
        if m2:
            meta_edition = m2.group(1)
        m3 = re.search(r"(Revision\s+\d+,\s*[A-Za-z]+\s+\d{4})", title_blob)
        if m3:
            meta_revision = m3.group(1)
    if rev_blob and not meta_revision:
        m3b = re.search(r"(Revision\s+\d+[^.,]*[A-Za-z]+\s+\d{4})", rev_blob)
        if m3b:
            meta_revision = m3b.group(1)

    # Per-role stats
    role_counts = {"title_page":0,"introduction":0,"revision_note":0,"toc":0,"body":0,"unknown":0}
    for s in sections:
        role_counts[s["role"]] = role_counts.get(s["role"],0) + 1

    small_chunks = sum(1 for c in chunks if c["char_count"] < 300)
    big_chunks   = sum(1 for c in chunks if c["char_count"] > 1400)
    lower_starts = sum(1 for c in chunks if c["text"] and c["text"][0].islower())

    # body-only metrics
    body_chunks = [c for c in chunks if c.get("role") == "body"]
    report = {
        "sections_total": len(sections),
        "sections_by_role": role_counts,
        "chunks_total": len(chunks),
        "chunks_body_only": len(body_chunks),
        "avg_chunk_chars": round(sum(c["char_count"] for c in chunks)/max(1,len(chunks)), 1) if chunks else 0,
        "avg_chunk_chars_body": round(sum(c["char_count"] for c in body_chunks)/max(1,len(body_chunks)), 1) if body_chunks else 0,
        "small_chunks_lt300": small_chunks,
        "big_chunks_gt1400": big_chunks,
        "chunks_starting_lowercase": lower_starts,
        "retrievable_sections": sum(1 for s in sections if s.get("retrievable", True)),
        "nonretrievable_sections": sum(1 for s in sections if not s.get("retrievable", True)),
        "params": {
            "target_chars": target_chars,
            "min_chars": min_chars,
            "overlap": overlap,
            "max_heading_level": max_heading_level
        }
    }

    index = {
        "schema_version": "3.0",
        "pipeline": {"name": "docx-indexer", "created_utc": now_iso()},
        "meta": {
            "source": "Federal Plain Language Guidelines (DOCX)",
            "docx_filename": docx.name,
            "doc_sha256": sha256_file(docx),
            "doc_title": meta_title,
            "edition": meta_edition,
            "revision": meta_revision
        },
        "outline": outline,     # H1–H3 for body
        "report": report,
        "sections": sections,   # includes non-retrievable regions
        "chunks": chunks        # body only
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    return index

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--docx", type=Path, required=True)
    ap.add_argument("--out",  type=Path, required=True)
    ap.add_argument("--target-chars", type=int, default=DEFAULT_TARGET)
    ap.add_argument("--min-chars",    type=int, default=DEFAULT_MIN)
    ap.add_argument("--overlap",      type=int, default=DEFAULT_OVERLAP)
    ap.add_argument("--max-heading-level", type=int, default=DEFAULT_MAXLVL)
    args = ap.parse_args()

    idx = build(args.docx, args.out, args.target_chars, args.min_chars, args.overlap, args.max_heading_level)
    r = idx["report"]
    print(f"Wrote {args.out}")
    print(f"Sections: {r['sections_total']} (retrievable: {r['retrievable_sections']}, non-retrievable: {r['nonretrievable_sections']})")
    print(f"By role: {r['sections_by_role']}")
    print(f"Chunks (all/body): {r['chunks_total']}/{r['chunks_body_only']}  avg(all/body)={r['avg_chunk_chars']}/{r['avg_chunk_chars_body']}")
    print(f"Small<300: {r['small_chunks_lt300']}  Big>1400: {r['big_chunks_gt1400']}  lowercase_starts: {r['chunks_starting_lowercase']}")
    print(f"Params: {r['params']}")

if __name__ == "__main__":
    main()
