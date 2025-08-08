from __future__ import annotations
import json, re
from pathlib import Path
from pypdf import PdfReader

def read_pdf(path: Path):
    reader = PdfReader(str(path))
    pages = []
    for p in reader.pages:
        t = p.extract_text() or ''
        t = re.sub(r'\s+\n', '\n', t)
        t = re.sub(r'[ \t]+', ' ', t)
        t = re.sub(r'\n{3,}', '\n\n', t)
        pages.append(t.strip())
    return pages

def chunk_text(pages, max_chars=1200, overlap=120):
    combined = '\n'.join(pages)
    paras = [p.strip() for p in combined.split('\n\n') if p.strip()]
    offsets, pos = [], 0
    for p in paras: offsets.append((pos, pos+len(p))); pos += len(p) + 2
    def pg(char):
        cum=0
        for i, page in enumerate(pages, start=1):
            cum2 = cum + len(page) + 1
            if char <= cum2: return i
            cum = cum2
        return len(pages)
    chunks, cur, cur_start = [], [], 0
    for i,p in enumerate(paras):
        if not cur: cur_start = offsets[i][0]
        if len('\n\n'.join(cur)) + len(p) <= max_chars:
            cur.append(p)
        else:
            text = '\n\n'.join(cur).strip()
            start, end = cur_start, cur_start + len(text)
            chunks.append({'id': f'chunk-{len(chunks):04d}', 'text': text,
                           'page_start': pg(start), 'page_end': pg(end),
                           'char_start': start, 'char_end': end})
            back = text[-overlap:]; cur = [back, p]; cur_start = max(0, end-overlap)
    if cur:
        text = '\n\n'.join(cur).strip()
        start, end = cur_start, cur_start + len(text)
        chunks.append({'id': f'chunk-{len(chunks):04d}', 'text': text,
                       'page_start': pg(start), 'page_end': pg(end),
                       'char_start': start, 'char_end': end})
    return chunks

if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--pdf', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    pages = read_pdf(args.pdf)
    chunks = chunk_text(pages)
    index = {'source':'Federal Plain Language Guidelines','pdf_filename':args.pdf.name,
             'num_pages':len(pages),'num_chunks':len(chunks),'chunks':chunks}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(index), encoding='utf-8')
    print(f'Wrote {args.out} with {len(chunks)} chunks.')
