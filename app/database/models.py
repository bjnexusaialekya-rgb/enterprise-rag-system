from sqlalchemy import Column, String, Integer, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from pgvector.sqlalchemy import Vector
import uuid
from datetime import datetime

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String, nullable=False)
    source = Column(String)
    department = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), nullable=False)
    content = Column(Text, nullable=False)
    chunk_index = Column(Integer)
    page_number = Column(Integer)
    department = Column(String)
    embedding = Column(Vector(384))
    created_at = Column(DateTime, default=datetime.utcnow)