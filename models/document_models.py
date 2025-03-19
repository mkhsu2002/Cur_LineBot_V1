from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

def DocumentModel(db):
    """Document model factory with correct db instance."""
    
    class Document(db.Model):
        """Model to store knowledge base documents for RAG"""
        __tablename__ = 'document'
        
        id = Column(Integer, primary_key=True)
        title = Column(String(128), nullable=False)
        content = Column(Text, nullable=False)
        filename = Column(String(128), nullable=True)
        uploaded_at = Column(DateTime, default=datetime.utcnow)
        updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        is_active = Column(Boolean, default=True)
        
        # 關聯會在初始化後設置
        chunks = None
        
        def __repr__(self):
            return f'<Document {self.title}>'
    
    return Document

def DocumentChunkModel(db):
    """Document chunk model factory with correct db instance."""
    
    class DocumentChunk(db.Model):
        """Model to store document chunks for vector search"""
        __tablename__ = 'document_chunk'
        
        id = Column(Integer, primary_key=True)
        document_id = Column(Integer, ForeignKey('document.id'), nullable=False)
        content = Column(Text, nullable=False)
        chunk_index = Column(Integer, nullable=False)
        
        # 關聯會在初始化後設置
        document = None
        
        def __repr__(self):
            return f'<DocumentChunk {self.id}>'
    
    return DocumentChunk 