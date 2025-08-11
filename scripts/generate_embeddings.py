
import json
from pathlib import Path
import argparse
from sentence_transformers import SentenceTransformer

def generate_embeddings(input_path: Path, output_path: Path):
    """
    Reads an index.json file, generates embeddings for each chunk,
    and saves the result to a new file.
    """
    print(f"Loading index from {input_path}...")
    with input_path.open("r", encoding="utf-8") as f:
        index_data = json.load(f)

    print("Loading sentence-transformer model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')

    chunks = index_data.get("chunks", [])
    print(f"Generating embeddings for {len(chunks)} chunks...")

    for i, chunk in enumerate(chunks):
        if i > 0 and i % 10 == 0:
            print(f"  Processed {i}/{len(chunks)} chunks...")
        chunk['embedding'] = model.encode(chunk['text']).tolist()
    
    print("Embeddings generated.")

    # Update some metadata
    if "meta" not in index_data:
        index_data["meta"] = {}
    index_data["meta"]["source"] = index_data["meta"].get("source", "Index") + " with Embeddings"
    if "report" not in index_data:
        index_data["report"] = {}
    if "params" not in index_data["report"]:
        index_data["report"]["params"] = {}
    index_data["report"]["params"]["embedding_model"] = 'all-MiniLM-L6-v2'


    print(f"Saving index with embeddings to {output_path}...")
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)
    
    print("Done.")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, required=True, help="Path to the input index.json file")
    ap.add_argument("--output", type=Path, required=True, help="Path to save the output file with embeddings")
    args = ap.parse_args()
    generate_embeddings(args.input, args.output)
