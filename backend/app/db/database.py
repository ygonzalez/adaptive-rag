from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import os
from typing import Generator
from contextlib import contextmanager

from .models import Base


class Database:
    def __init__(self):
        # Get PostgreSQL database URL from environment
        self.database_url = os.getenv("DATABASE_URL")
        
        if not self.database_url:
            raise ValueError(
                "DATABASE_URL environment variable is required. "
                "Please set it to your PostgreSQL connection string: "
                "postgresql://user:password@host:port/database"
            )
        
        # Handle PostgreSQL URL format from some cloud providers
        if self.database_url.startswith("postgres://"):
            self.database_url = self.database_url.replace("postgres://", "postgresql://", 1)
        
        # Validate PostgreSQL URL
        if not self.database_url.startswith("postgresql://"):
            raise ValueError(
                "DATABASE_URL must be a PostgreSQL connection string starting with 'postgresql://'"
            )
        
        # Create engine with PostgreSQL settings
        self.engine = create_engine(
            self.database_url,
            pool_pre_ping=True,
            pool_recycle=300,
            pool_size=10,
            max_overflow=20,
        )
        
        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
    
    def create_tables(self):
        """Create all tables in the database"""
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self) -> Generator[Session, None, None]:
        """Dependency to get database session"""
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    @contextmanager
    def session_scope(self):
        """Provide a transactional scope for database operations"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


# Global database instance
db = Database()