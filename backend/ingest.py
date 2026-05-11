# backend/ingest.py
import json
import os
from sentence_transformers import SentenceTransformer
import chromadb
from dotenv import load_dotenv

load_dotenv()

embedder = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection("torah_texts")

def chunk_text(text, source, chunk_size=400, overlap=50):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append({"text": chunk, "source": source})
    return chunks

def ingest_json(filepath):
    with open(filepath) as f:
        data = json.load(f)
    
    # Sefaria stores English text in "text" field
    text_data = data.get("text", [])
    
    # Flatten nested lists (some books are nested)
    def flatten(lst):
        result = []
        for item in lst:
            if isinstance(item, list):
                result.extend(flatten(item))
            elif isinstance(item, str) and item.strip():
                result.append(item)
        return result
    
    passages = flatten(text_data)
    full_text = " ".join(passages)
    source_name = data.get("book", filepath)
    
    chunks = chunk_text(full_text, source=source_name)
    
    texts = [c["text"] for c in chunks]
    embeddings = embedder.encode(texts, show_progress_bar=True).tolist()
    ids = [f"{source_name}_{i}" for i in range(len(chunks))]
    metadatas = [{"source": c["source"]} for c in chunks]
    
    collection.add(
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas,
        ids=ids
    )
    print(f"✅ Ingested {source_name}: {len(chunks)} chunks")

if __name__ == "__main__":
    folder = "./data/texts"
    for filename in os.listdir(folder):
        if filename.endswith(".json"):
            ingest_json(f"{folder}/{filename}")
    print("✅ All done! chroma_db is ready.")