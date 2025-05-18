# python_ui/database/db_handler.py

import sqlite3
import os

DB_PATH = "python_ui/database/exam_records.sqlite"

def init_db():
    """Initializes the database and creates tables if not exist."""
    if not os.path.exists("python_ui/database"):
        os.makedirs("python_ui/database")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS exam_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            score INTEGER NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

def save_exam_result(student_id, score):
    """Saves a student's exam score."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO exam_results (student_id, score) VALUES (?, ?)
    """, (student_id, score))

    conn.commit()
    conn.close()

def get_all_results():
    """Returns all stored exam results."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM exam_results")
    results = cursor.fetchall()

    conn.close()
    return results


# For initial setup
if __name__ == "__main__":
    init_db()
    print("✅ Database initialized.")
