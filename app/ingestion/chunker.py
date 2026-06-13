from typing import List, Dict

def chunk_text(text: str, chunk_size: int = 150, overlap: int = 20) -> List[Dict]:
    words = text.split()
    chunks = []
    index = 0

    i = 0
    while i < len(words):
        chunk_words = words[i:i + chunk_size]
        chunk_text = " ".join(chunk_words)
        chunks.append({
            "content": chunk_text,
            "chunk_index": index,
            "word_count": len(chunk_words)
        })
        index += 1
        i += chunk_size - overlap

    return chunks


def chunk_document(filename: str, text: str, department: str = "general") -> List[Dict]:
    chunks = chunk_text(text)
    for chunk in chunks:
        chunk["filename"] = filename
        chunk["department"] = department
    return chunks