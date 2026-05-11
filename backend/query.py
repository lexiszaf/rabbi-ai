# backend/query.py
import os
from sentence_transformers import SentenceTransformer
import chromadb
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

embedder = SentenceTransformer("all-MiniLM-L6-v2")
chroma = chromadb.PersistentClient(path="./chroma_db")
collection = chroma.get_collection("torah_texts")
groq_client = Groq(api_key=os.environ["GROQ_API_KEY"])

SYSTEM_PROMPT = """You are an Orthodox rabbi, knowledgeable in halacha, Talmud, Torah, and Jewish philosophy. 
Answer questions directly and substantively, drawing from classical Jewish sources.
You may use Hebrew and Aramaic terms where appropriate (e.g. mitzvot, chesed, mussar, b'ezrat Hashem) but always explain them briefly if they are central to the answer.
Cite sources precisely when possible — e.g. "The Rambam writes in Hilchot De'ot..." or "As the Gemara in Shabbat 31a states..."
Be direct, grounded, and serious — like a rav answering a she'ela.
Try to speak like an actual orthodox rabbi in your tone, not like a robot. You can use terms a rabbi would use, and you can be warm and encouraging when appropriate. You can use terms a rabbi would use that are practical in Halacha, like She'ela (answer), or a term of encouragement like "b'ezrat Hashem" or "l'chaim". But avoid being overly flowery or poetic. Be clear and direct.
Don't use the term My child or anything lovey dovey like that. You are a rabbi, not a mother or a god.
If the provided texts don't address the question, say so plainly and offer what general Torah perspective you can. Make answers feel direct and personal, don't give overall impersonal answers. Address the asker as "you" not saying "someone should". If the question is about a specific situation, try to address that situation directly and practically, not just giving general information."""
def ask(question: str, history: list = []) -> dict:
    print(f"DEBUG history length: {len(history)}", flush=True)  # add this line
    
    # For short follow-ups, combine with previous question for better retrieval
    retrieval_query = question
    if history and len(question.split()) < 8:
        retrieval_query = f"{history[-1]['user']} {question}"
    
    q_embedding = embedder.encode([retrieval_query]).tolist()[0]
    
    results = collection.query(
        query_embeddings=[q_embedding],
        n_results=5
    )
    
    context_chunks = results["documents"][0]
    sources = [m["source"] for m in results["metadatas"][0]]
    context = "\n\n---\n\n".join(
        [f"[{sources[i]}]\n{chunk}" for i, chunk in enumerate(context_chunks)]
    )

    # Build messages with history
    messages = []
    for turn in history:
        messages.append({"role": "user", "content": turn["user"]})
        messages.append({"role": "assistant", "content": turn["rabbi"]})
    
    # Add current question with context
    messages.append({
        "role": "user",
        "content": f"Sources:\n{context}\n\nQuestion: {question}"
    })

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages,
        max_tokens=1024,
        temperature=0.3
    )
    
    return {
        "answer": response.choices[0].message.content,
        "sources": list(set(sources))
    }

# Quick test
if __name__ == "__main__":
    result = ask("What does Jewish wisdom say about being a good person?")
    print("\n🤖 Rabbi says:\n")
    print(result["answer"])
    print("\n📚 Sources:", result["sources"])