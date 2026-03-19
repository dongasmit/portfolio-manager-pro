"""Document upload and RAG query endpoints."""
import os
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Document
from app.rag.pipeline import rag_pipeline, UPLOAD_DIR

router = APIRouter()


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    doc_type: str = Form("sebi_circular"),
    db: Session = Depends(get_db),
):
    """Upload a PDF/text document for RAG ingestion."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    doc_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename)[1].lower()

    if ext not in (".pdf", ".txt"):
        raise HTTPException(status_code=400, detail="Only PDF and TXT files supported")

    # Save file
    filepath = os.path.join(UPLOAD_DIR, f"{doc_id}{ext}")
    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)

    # Create DB record
    doc = Document(
        id=doc_id,
        filename=file.filename,
        doc_type=doc_type,
    )
    db.add(doc)
    db.commit()

    # Ingest into vector store
    if ext == ".pdf":
        chunk_count = rag_pipeline.ingest_pdf(filepath, doc_id, doc_type, db)
    else:
        text = content.decode("utf-8", errors="ignore")
        chunk_count = rag_pipeline.ingest_text(
            doc_id, text, {"doc_id": doc_id, "doc_type": doc_type, "filename": file.filename}
        )
        doc.chunk_count = chunk_count
        doc.content_summary = text[:500]
        db.commit()

    return {
        "doc_id": doc_id,
        "filename": file.filename,
        "doc_type": doc_type,
        "chunks_created": chunk_count,
    }


@router.get("/")
def list_documents(db: Session = Depends(get_db)):
    """List all uploaded documents."""
    docs = db.query(Document).order_by(Document.uploaded_at.desc()).all()
    return [
        {
            "id": d.id,
            "filename": d.filename,
            "doc_type": d.doc_type,
            "content_summary": d.content_summary,
            "chunk_count": d.chunk_count,
            "uploaded_at": str(d.uploaded_at),
        }
        for d in docs
    ]


@router.post("/query")
def query_documents(question: str = Form(...), doc_type: str = Form(None)):
    """Query the RAG pipeline."""
    results = rag_pipeline.query(question, doc_type=doc_type)
    return {"question": question, "results": results}


@router.get("/stats")
def rag_stats():
    """Get RAG pipeline statistics."""
    return rag_pipeline.get_stats()
