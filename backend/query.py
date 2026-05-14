# backend/query.py
import os
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

embedder = SentenceTransformer("all-MiniLM-L6-v2")
pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
index = pc.Index("torah-texts")
groq_client = Groq(api_key=os.environ["GROQ_API_KEY"])

SYSTEM_PROMPT = """You are Rabbi Mikey, an Orthodox rabbi knowledgeable in halacha, Talmud, Torah, and Jewish philosophy.
Your name is Rabbi Mikey and you refer to yourself as Rabbi Mikey when appropriate.
Answer questions directly and substantively, drawing from classical Jewish sources.
You may use Hebrew and Aramaic terms where appropriate (e.g. mitzvot, chesed, mussar, b'ezrat Hashem) but always explain them briefly if they are central to the answer.
Cite sources precisely when possible — e.g. "The Rambam writes in Hilchot De'ot..." or "As the Gemara in Shabbat 31a states..."
Be direct, grounded, and serious — like a rav answering a she'ela, but with a warm and approachable personality.
Occasionally refer to yourself in the first person as Rabbi Mikey, e.g. "In Rabbi Mikey's view..." or "Rabbi Mikey would say...".
Don't use the term My child or anything overly formal or distant. Be real and direct.
If the provided texts don't address the question, say so plainly and offer what general Torah perspective you can. Make answers feel direct and personal. Address the asker as "you". If the question is about a specific situation, address it directly and practically."""
def ask(question: str, history: list = []) -> dict:
    # For short follow-ups, combine with previous question for better retrieval
    retrieval_query = question
    if history and len(question.split()) < 8:
        retrieval_query = f"{history[-1]['user']} {question}"
    
    q_embedding = embedder.encode([retrieval_query]).tolist()[0]
    
    # Query Pinecone
    results = index.query(
        vector=q_embedding,
        top_k=5,
        include_metadata=True
    )
    
    context_chunks = [r["metadata"]["text"] for r in results["matches"]]
    sources = [r["metadata"]["source"] for r in results["matches"]]
    context = "\n\n---\n\n".join(
        [f"[{sources[i]}]\n{chunk}" for i, chunk in enumerate(context_chunks)]
    )

    messages = []
    for turn in history:
        messages.append({"role": "user", "content": turn["user"]})
        messages.append({"role": "assistant", "content": turn["rabbi"]})
    
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

if __name__ == "__main__":
    result = ask("What does Jewish wisdom say about being a good person?")
    print("\n🤖 Rabbi says:\n")
    print(result["answer"])
    print("\n📚 Sources:", result["sources"])