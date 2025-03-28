"""
database.py: Handles SQL database interactions for storing search results and metadata.
Uses SQLAlchemy for ORM.
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

Base = declarative_base()

class SearchResult(Base):
    __tablename__ = 'search_results'
    
    id = Column(Integer, primary_key=True)
    ref_id = Column(String(10), unique=True, nullable=False)
    pmid = Column(String(20), nullable=False)
    title = Column(Text, nullable=False)
    authors = Column(Text)
    abstract = Column(Text)
    doi = Column(String(100))
    link = Column(Text)
    year = Column(Integer)

class Metadata(Base):
    __tablename__ = 'metadata'
    
    id = Column(Integer, primary_key=True)
    min_year = Column(Integer, nullable=False)
    max_year = Column(Integer, nullable=False)
    research_purpose = Column(Text, nullable=False)
    mesh_strategy = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db(db_url: str = "sqlite:///search.db"):
    """
    Initialize the database and return the engine.
    """
    engine = create_engine(db_url, echo=False)
    Base.metadata.create_all(engine)
    return engine

def get_engine_session(engine):
    """
    Return a new SQLAlchemy session.
    """
    Session = sessionmaker(bind=engine)
    return Session()

def store_metadata(session, min_year, max_year, research_purpose, mesh_strategy):
    """
    Store metadata in the database.
    """
    metadata = Metadata(
        min_year=min_year,
        max_year=max_year,
        research_purpose=research_purpose,
        mesh_strategy=mesh_strategy
    )
    session.add(metadata)
    session.flush()  # Flush to assign an ID if needed

def store_search_results(session, articles):
    """
    Store search results in the database.
    Generates a unique RefID for each article.
    """
    for idx, article in enumerate(articles, start=1):
        ref_id = f"S{idx:05d}"
        article["RefID"] = ref_id
        result = SearchResult(
            ref_id=ref_id,
            pmid=article.get("PMID", "N/A"),
            title=article.get("Title", "No Title"),
            authors=article.get("Authors", "No Authors"),
            abstract=article.get("Abstract", "No Abstract"),
            doi=article.get("DOI", "N/A"),
            link=article.get("Link", "N/A"),
            year=article.get("Year", 0)
        )
        session.add(result)
