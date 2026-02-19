"""
models.py
SQLAlchemy ORM models for SAR Generator.
This file defines the database schema using declarative models.
Note: The current implementation uses raw SQL in database.py for simplicity.
This file is provided for reference and future ORM migration.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Case(Base):
    """
    SAR Case model - stores every suspicious activity report case.
    """
    __tablename__ = 'cases'

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_name = Column(String(255), nullable=False)
    account_number = Column(String(100), nullable=False)
    transactions = Column(Text, nullable=False)
    sar_narrative = Column(Text)
    status = Column(String(50), default='DRAFT')  # DRAFT, APPROVED, REJECTED
    analyst_name = Column(String(255))
    created_at = Column(String(50))
    approved_at = Column(String(50))
    approved_by = Column(String(255))
    edited_narrative = Column(Text)
    risk_score = Column(Integer, default=0)
    typology = Column(String(255))

    # Relationship to audit logs
    audit_logs = relationship("AuditLog", back_populates="case", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Case(id={self.id}, customer='{self.customer_name}', status='{self.status}')>"


class AuditLog(Base):
    """
    Audit Log model - tracks every action taken on every case.
    This is critical for regulatory compliance and explainability.
    """
    __tablename__ = 'audit_log'

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(Integer, ForeignKey('cases.id'), nullable=False)
    action = Column(String(100), nullable=False)  # SAR_GENERATED, SAR_APPROVED, etc.
    analyst = Column(String(255))
    detail = Column(Text)
    timestamp = Column(String(50))
    data_used = Column(Text)  # JSON string of what data/model was used

    # Relationship to case
    case = relationship("Case", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog(id={self.id}, case_id={self.case_id}, action='{self.action}')>"


class SARTemplate(Base):
    """
    SAR Template model - stores example SAR narratives for RAG retrieval.
    These are loaded into ChromaDB but also stored here for reference.
    """
    __tablename__ = 'sar_templates'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255))
    typology = Column(String(255))
    template = Column(Text)
    created_at = Column(String(50))

    def __repr__(self):
        return f"<SARTemplate(id={self.id}, typology='{self.typology}')>"


# Optional: Helper function to create all tables using ORM
def create_tables(engine):
    """
    Create all tables defined by the ORM models.
    Usage:
        from sqlalchemy import create_engine
        from models import create_tables
        
        engine = create_engine('sqlite:///sar_cases.db')
        create_tables(engine)
    """
    Base.metadata.create_all(engine)
    print("✅ All tables created via ORM models.")


# Optional: Helper function to get session
def get_session(engine):
    """
    Get a database session for ORM operations.
    Usage:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from models import get_session
        
        engine = create_engine('sqlite:///sar_cases.db')
        Session = sessionmaker(bind=engine)
        session = Session()
    """
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    return Session()