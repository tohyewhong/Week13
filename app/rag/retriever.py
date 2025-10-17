
import os
from pathlib import Path
import re
from typing import List, Dict, Any

from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from ..utils.config import settings

class Retriever:
    def __init__(self, index_dir: str, model_name: str):
        self.docs_dir = "data/docs"
        self._load_documents()
        self._build_index()
    
    def _load_documents(self):
        """Load all text documents from the docs directory"""
        self.documents = []
        docs_path = Path(self.docs_dir)
        
        if docs_path.exists():
            for file_path in docs_path.glob("*.txt"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if content:
                            self.documents.append({
                                "text": content,
                                "source": file_path.name,
                                "file_path": str(file_path)
                            })
                except Exception as e:
                    print(f"Error loading {file_path}: {e}")

    def _build_index(self):
        # Split into chunks
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        chunks: List[Dict[str, Any]] = []
        for d in self.documents:
            for ch in splitter.split_text(d["text"]):
                chunks.append({"text": ch, "source": d["source"]})

        if not chunks:
            self.vs = None
            return

        # Build FAISS with OpenAI embeddings
        embeddings = OpenAIEmbeddings(model=settings.OPENAI_EMBEDDINGS_MODEL)
        texts = [c["text"] for c in chunks]
        metadatas = [{"source": c["source"]} for c in chunks]
        self.vs = FAISS.from_texts(texts=texts, embedding=embeddings, metadatas=metadatas)
    
    def search(self, query: str, k: int = 4):
        if getattr(self, "vs", None) is None:
            return [{"text": "No index available.", "meta": {"source": "system"}, "score": 0.0}]

        docs = self.vs.similarity_search_with_score(query, k=k)
        results = []
        for doc, score in docs:
            results.append({
                "text": doc.page_content,
                "meta": {"source": doc.metadata.get("source", "unknown")},
                "score": float(score) if score is not None else 0.0,
            })
        return results
