#!/usr/bin/env python3
"""
Database initialization script for Adaptive RAG
Creates all tables and optionally seeds with sample data
"""

import os
import sys
from pathlib import Path

# Add backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables BEFORE importing database modules
from dotenv import load_dotenv
load_dotenv()

from app.db.database import db
from app.db.models import Base, ChatSession, ChatMessage
from sqlalchemy import text


def init_database():
    """Initialize the database with tables"""
    print("Initializing PostgreSQL database...")
    
    # Mask password in URL for display
    display_url = db.database_url.replace(
        db.database_url.split('@')[0].split('://')[-1].split(':')[-1], 
        '***'
    ) if '@' in db.database_url else db.database_url
    print(f"Database URL: {display_url}")
    
    try:
        # Test connection first
        print("Testing database connection...")
        db.engine.connect()
        print("✅ Successfully connected to PostgreSQL!")
        
        # Create all tables
        print("Creating tables...")
        Base.metadata.create_all(bind=db.engine)
        print("✅ Database tables created successfully!")
        
        # Show table information
        with db.session_scope() as session:
            # Check if tables exist
            result = session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name;
            """))
            tables = [row[0] for row in result]
            print(f"📋 Tables in database: {', '.join(tables)}")
            
            # Get current stats
            session_count = session.query(ChatSession).count()
            message_count = session.query(ChatMessage).count()
            print(f"📊 Current stats: {session_count} sessions, {message_count} messages")
            
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        print("\n💡 Troubleshooting tips:")
        print("1. Ensure PostgreSQL is running")
        print("2. Check your DATABASE_URL in .env file")
        print("3. Run ./setup_postgres.sh to create the database and user")
        print("4. Verify you can connect with: psql -U yvettegonzalez -d adaptive_rag_db")
        sys.exit(1)


def seed_sample_data():
    """Optionally seed the database with sample data"""
    with db.session_scope() as session:
        # Check if we already have data
        if session.query(ChatSession).count() > 0:
            print("Database already contains data, skipping seed")
            return
        
        # Create a sample session
        sample_session = ChatSession(id="sample-session-1")
        session.add(sample_session)
        
        # Add sample messages
        sample_messages = [
            ChatMessage(
                session_id="sample-session-1",
                question="What is Adaptive RAG?",
                answer="Adaptive RAG is a retrieval-augmented generation system that intelligently combines vector database retrieval with web search to provide accurate answers.",
                used_web_search=False,
                sources=[{
                    "content": "Adaptive RAG combines retrieval and generation...",
                    "metadata": {"source": "vectorstore"}
                }]
            ),
            ChatMessage(
                session_id="sample-session-1",
                question="How to make pizza?",
                answer="To make pizza, you'll need dough, sauce, cheese, and toppings. Start by preparing the dough...",
                used_web_search=True,
                sources=[{
                    "content": "Pizza making involves several steps...",
                    "metadata": {"source": "web"}
                }]
            )
        ]
        
        for msg in sample_messages:
            session.add(msg)
        
        print("✅ Sample data seeded successfully!")


if __name__ == "__main__":
    init_database()
    
    # Optionally seed sample data
    if "--seed" in sys.argv:
        seed_sample_data()