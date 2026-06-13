import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are an enterprise assistant. Answer questions using ONLY the provided context below.
For each fact you state, cite the source like: (Source: filename.pdf)
If the context does not contain enough information, say: "I don't have enough information to answer this question."
Never hallucinate. Never use outside knowledge."""


def generate_answer(query: str, validated_chunks: list[dict]) -> dict:
    if not validated_chunks:
        return {
            "answer": "I don't have enough information to answer this question.",
            "sources": [],
            "chunks_used": 0
        }

    context_parts = []
    sources = []
    for i, chunk in enumerate(validated_chunks, 1):
        filename = chunk.get("filename", "unknown")
        context_parts.append(f"[{i}] (Source: {filename})\n{chunk['content']}")
        sources.append({
            "chunk_id":   chunk.get("chunk_id"),
            "document_id": chunk.get("document_id"),
            "filename":   filename,
            "score":      round(float(chunk.get("score", 0)), 4),
            "preview":    chunk.get("content", "")[:150]
        })

    context = "\n\n".join(context_parts)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
    ]

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.1,
        max_tokens=1024
    )

    return {
        "answer": response.choices[0].message.content,
        "sources": sources,
        "chunks_used": len(validated_chunks),
        "model": response.model,
        "usage": {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens
        }
    }
