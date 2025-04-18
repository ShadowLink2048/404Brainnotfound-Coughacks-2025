import sqlite3
from datetime import datetime
import os

# Always resolve path relative to this script's directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "database", "pocketlawyer.db")


def load_pii_keywords():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT keyword, pii_type FROM pii_keywords")
    keywords = cursor.fetchall()

    conn.close()
    return keywords

# Scanner Function

def scan_text_for_pii(document_id, text):
    keywords = load_pii_keywords()
    results = []

    for keyword, pii_type in keywords:
        if keyword.lower() in text.lower():
            # Grab snippet of surrounding text
            start = text.lower().find(keyword.lower())
            snippet = text[max(0, start-30):start+len(keyword)+30]

            results.append((document_id, pii_type, snippet.strip()))

    return results # List of (doc_id, pii_type, snippet)


# Save matches to detected_pii
def save_pii_results(results):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for document_id, pii_type, snippet in results:
        cursor.execute("""
            INSERT INTO detected_pii (document_id, pii_type, context_snippet)
            VALUES (?, ?, ?)
        """, (document_id, pii_type, snippet))

    conn.commit()
    conn.close()

