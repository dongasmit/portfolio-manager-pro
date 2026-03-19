"""RAG pipeline for SEBI compliance documents and earnings reports."""
import os
from typing import Optional
from sqlalchemy.orm import Session

from app.models.models import Document
from app.config import get_settings

settings = get_settings()

# Directory for ChromaDB persistence
CHROMA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "chroma_db")
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")

os.makedirs(CHROMA_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)


class RAGPipeline:
    """
    RAG pipeline that:
    1. Ingests PDF/text documents (SEBI circulars, earnings reports, risk guidelines)
    2. Chunks and embeds them into ChromaDB
    3. Retrieves relevant context for AI agent queries
    """

    def __init__(self):
        self._collection = None
        self._client = None

    def _get_collection(self):
        """Lazy-initialize ChromaDB collection."""
        if self._collection is None:
            try:
                import chromadb
                self._client = chromadb.PersistentClient(path=CHROMA_DIR)
                self._collection = self._client.get_or_create_collection(
                    name="financial_documents",
                    metadata={"hnsw:space": "cosine"},
                )
            except Exception as e:
                print(f"ChromaDB init error: {e}")
                return None
        return self._collection

    def ingest_text(self, doc_id: str, text: str, metadata: dict, chunk_size: int = 1000) -> int:
        """Chunk and embed text into the vector store."""
        collection = self._get_collection()
        if collection is None:
            return 0

        # Simple chunking by character count with overlap
        chunks = []
        overlap = 200
        for i in range(0, len(text), chunk_size - overlap):
            chunk = text[i : i + chunk_size]
            if chunk.strip():
                chunks.append(chunk)

        if not chunks:
            return 0

        ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [{**metadata, "chunk_index": i} for i in range(len(chunks))]

        collection.upsert(
            ids=ids,
            documents=chunks,
            metadatas=metadatas,
        )
        return len(chunks)

    def ingest_pdf(self, filepath: str, doc_id: str, doc_type: str, db: Session) -> int:
        """Ingest a PDF file into the vector store."""
        try:
            from pypdf import PdfReader
            reader = PdfReader(filepath)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
        except Exception as e:
            print(f"PDF read error: {e}")
            return 0

        metadata = {
            "doc_id": doc_id,
            "doc_type": doc_type,
            "filename": os.path.basename(filepath),
        }

        chunk_count = self.ingest_text(doc_id, text, metadata)

        # Update document record
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if doc:
            doc.chunk_count = chunk_count
            doc.content_summary = text[:500] + "..." if len(text) > 500 else text
            db.commit()

        return chunk_count

    def query(self, question: str, n_results: int = 5, doc_type: Optional[str] = None) -> list[dict]:
        """Query the vector store for relevant document chunks."""
        collection = self._get_collection()
        if collection is None:
            return []

        where_filter = None
        if doc_type:
            where_filter = {"doc_type": doc_type}

        try:
            results = collection.query(
                query_texts=[question],
                n_results=n_results,
                where=where_filter,
            )
        except Exception:
            # If no documents yet
            return []

        documents = []
        if results and results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                meta = results["metadatas"][0][i] if results["metadatas"] else {}
                distance = results["distances"][0][i] if results["distances"] else 0
                documents.append({
                    "content": doc,
                    "metadata": meta,
                    "relevance_score": round(1 - distance, 4),
                })

        return documents

    def get_stats(self) -> dict:
        """Get collection statistics."""
        collection = self._get_collection()
        if collection is None:
            return {"status": "not_initialized", "count": 0}
        return {
            "status": "ready",
            "count": collection.count(),
        }


# Singleton
rag_pipeline = RAGPipeline()
