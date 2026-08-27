from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Float, Text
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime


Base = declarative_base()

class Appeal(Base):
    __tablename__ = "appeals"
    
    id = Column(Integer, primary_key=True, index=True)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    input_type = Column(String) # 'text', 'link', 'image'
    raw_content = Column(String) # the text, URL, or image path
    
    text_embedding = Column(String) # Assuming sentence-transformers all-MiniLM-L6-v2
    image_hash = Column(String, nullable=True) # Perceptual hash for images
    
    entities = relationship("ExtractedEntity", back_populates="appeal")
    verifications = relationship("VerificationResult", back_populates="appeal")
    report = relationship("TrustReport", uselist=False, back_populates="appeal")

class ExtractedEntity(Base):
    __tablename__ = "extracted_entities"
    
    id = Column(Integer, primary_key=True, index=True)
    appeal_id = Column(Integer, ForeignKey("appeals.id"))
    entity_type = Column(String) # 'ORG', 'PAYMENT_ID', 'URL', 'CLAIM'
    entity_value = Column(String)
    
    appeal = relationship("Appeal", back_populates="entities")

class VerificationResult(Base):
    __tablename__ = "verification_results"
    
    id = Column(Integer, primary_key=True, index=True)
    appeal_id = Column(Integer, ForeignKey("appeals.id"))
    module_name = Column(String) # 'Identity', 'Payment', 'Similarity', 'Claim'
    status = Column(String) # 'Verified', 'Unverifiable', 'Flagged'
    confidence = Column(Float)
    details = Column(String) # JSON string of detailed findings
    
    appeal = relationship("Appeal", back_populates="verifications")

class TrustReport(Base):
    __tablename__ = "trust_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    appeal_id = Column(Integer, ForeignKey("appeals.id"))
    score = Column(Integer) # out of 100
    summary = Column(String)
    evidence_graph = Column(Text, nullable=True)  # JSON string of the evidence graph
    
    appeal = relationship("Appeal", back_populates="report")
