"""
database.py: Handles SQL database interactions for storing search results and metadata.
Uses SQLAlchemy for ORM.
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class SearchResult(Base):
    __tablename__ = 'search_results'
    
    id = Column(Integer, primary_key=True)
    pmid = Column(String(20))
    title = Column(Text)
    authors = Column(Text)
    abstract = Column(Text)
    doi = Column(String(100))
    link = Column(Text)
    year = Column(Integer)
    metadata_id = Column(Integer, ForeignKey('metadata.id'))
    search_metadata = relationship("Metadata", back_populates="search_results")

class Metadata(Base):
    __tablename__ = 'metadata'
    
    id = Column(Integer, primary_key=True)
    min_year = Column(Integer, nullable=False)
    max_year = Column(Integer, nullable=False)
    research_purpose = Column(Text, nullable=False)
    mesh_strategy = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    search_results = relationship("SearchResult", back_populates="search_metadata")

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
    return metadata.id

def store_search_results(session, articles, metadata_id):
    """
    Store search results in the database.
    Links each result to the corresponding metadata entry.
    """
    for article in articles:
        result = SearchResult(
            pmid=article.get("PMID", "N/A"),
            title=article.get("Title", "No Title"),
            authors=article.get("Authors", "No Authors"),
            abstract=article.get("Abstract", "No Abstract"),
            doi=article.get("DOI", "N/A"),
            link=article.get("Link", "N/A"),
            year=article.get("Year", 0),
            metadata_id = metadata_id
        )
        session.add(result)
