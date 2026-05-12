# backend/ingest.py
import json
import os
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()

embedder = SentenceTransformer("all-MiniLM-L6-v2")

pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
index = pc.Index("torah-texts")

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
    
    text_data = data.get("text", [])
    
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
    source_name = data.get("book", os.path.basename(filepath))
    
    chunks = chunk_text(full_text, source=source_name)
    
    # Pinecone upserts in batches of 100
    batch_size = 100
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        texts = [c["text"] for c in batch]
        embeddings = embedder.encode(texts).tolist()
        
        vectors = [
            {
                "id": f"{source_name}_{i + j}",
                "values": embeddings[j],
                "metadata": {"source": source_name, "text": texts[j]}
            }
            for j in range(len(batch))
        ]
        
        index.upsert(vectors=vectors)
    
    print(f"✅ Ingested {source_name}: {len(chunks)} chunks")

if __name__ == "__main__":
    folder = "./data/texts"
    for filename in os.listdir(folder):
        if filename.endswith(".json"):
            ingest_json(f"{folder}/{filename}")
    print("✅ All done! Pinecone index is ready.")