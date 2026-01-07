import sqlite3
import datetime
import json
from typing import List, Dict, Any

# Define the database file path. This file will be created 
# in your project directory upon the first run.
DB_FILE = 'feedback.db'

def init_db():
    """Create the required tables: 'feedback' and 'chat_sessions'."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # 1. Table for Feedback 
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                rating INTEGER NOT NULL,
                comment TEXT,
                conversation_log TEXT 
            )
        ''')

        # 2. Table for Persistent Chat Sessions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                messages TEXT -- Full conversation log as JSON
            )
        ''')

        conn.commit()
        conn.close()
        print("Application database (feedback.db) initialized with both tables.")
    except Exception as e:
        print(f"Error initializing database: {e}")

def save_user_feedback(rating: int, comment: str, conversation_history: List[Dict[str, Any]]):
    """Saves structured feedback to the 'feedback' table."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        timestamp = datetime.datetime.now().isoformat()
        conversation_json = json.dumps(conversation_history)
        
        cursor.execute(
            '''INSERT INTO feedback (timestamp, rating, comment, conversation_log) 
               VALUES (?, ?, ?, ?)''',
            (timestamp, rating, comment, conversation_json)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving feedback: {e}")
        return False

def save_chat_session(title: str, messages: List[Dict[str, Any]]):
    """Saves a completed conversation to the 'chat_sessions' table."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        timestamp = datetime.datetime.now().isoformat()
        messages_json = json.dumps(messages)
        
        cursor.execute(
            '''INSERT INTO chat_sessions (title, timestamp, messages) 
               VALUES (?, ?, ?)''',
            (title, timestamp, messages_json)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving chat session: {e}")
        return False

def load_chat_sessions():
    """Loads all chat session IDs, titles, and timestamps for the sidebar."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, title, timestamp FROM chat_sessions ORDER BY id DESC'
        )
        sessions = cursor.fetchall()
        conn.close()
        return sessions
    except Exception as e:
        print(f"Error loading chat sessions: {e}")
        return []

def load_session_messages(session_id: int):
    """Loads the full message log for a specific session ID."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            'SELECT messages FROM chat_sessions WHERE id = ?', (session_id,)
        )
        messages_json = cursor.fetchone()
        conn.close()
        if messages_json:
            return json.loads(messages_json[0])
        return []
    except Exception as e:
        print(f"Error loading messages for session {session_id}: {e}")
        return []

# Initialize the database immediately when this module is imported
init_db()