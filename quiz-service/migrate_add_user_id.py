"""
Migration script to add user_id column to quiz_attempts table.
Run this once to add the column to existing database.
"""
import os
from dotenv import load_dotenv
from sqlalchemy import inspect, text
from app import create_app
from app.db import db

load_dotenv()

def migrate():
    app = create_app()
    with app.app_context():
        # Check if column already exists
        inspector = inspect(db.engine)
        if not inspector.has_table('quiz_attempts'):
            print("Table 'quiz_attempts' does not exist yet. It will be created on next app start.")
            return
        
        columns = [col['name'] for col in inspector.get_columns('quiz_attempts')]
        
        if 'user_id' in columns:
            print("✓ Column 'user_id' already exists in quiz_attempts table")
            return
        
        # Add the column using raw SQL
        try:
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE quiz_attempts ADD COLUMN user_id INTEGER"))
                conn.commit()
            print("✓ Successfully added 'user_id' column to quiz_attempts table")
        except Exception as e:
            # Column might already exist or other error
            print(f"Note: {e}")
            print("Column may already exist or there was an issue. Continuing...")

if __name__ == "__main__":
    migrate()

