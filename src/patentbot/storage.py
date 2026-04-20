"""
Storage module - SQLite database operations
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Any

DB_PATH = Path("patents.db")

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database() -> sqlite3.Connection:
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patents (
            patent_number TEXT PRIMARY KEY,
            title TEXT,
            abstract TEXT,
            assignee TEXT,
            inventors TEXT,
            filing_date DATE,
            grant_date DATE,
            forward_citations TEXT,
            backward_citations TEXT,
            sources TEXT,
            fetched_at TIMESTAMP,
            summarized_at TIMESTAMP,
            summary TEXT,
            key_problem TEXT,
            key_solution TEXT,
            tags TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS citations (
            citing_patent TEXT,
            cited_patent TEXT,
            family_cite BOOLEAN,
            direction TEXT,
            PRIMARY KEY (citing_patent, cited_patent, direction)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            name TEXT PRIMARY KEY,
            aliases TEXT,
            last_indexed TIMESTAMP
        )
    """)
    
    conn.commit()
    return conn

def save_patent(patent_data: dict[str, Any]) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR REPLACE INTO patents (
            patent_number, title, abstract, assignee, inventors, filing_date, grant_date,
            forward_citations, backward_citations, sources, fetched_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        patent_data.get("patent_number"),
        patent_data.get("title"),
        patent_data.get("abstract"),
        patent_data.get("assignee"),
        json.dumps(patent_data.get("inventors", [])),
        patent_data.get("filing_date"),
        patent_data.get("grant_date"),
        json.dumps(patent_data.get("forward_citations", [])),
        json.dumps(patent_data.get("backward_citations", [])),
        json.dumps(patent_data.get("sources", [])),
        datetime.now().isoformat()
    ))
    
    # Save citations
    pn = patent_data.get("patent_number")
    for cited in patent_data.get("forward_citations", []):
        cursor.execute("""
            INSERT OR IGNORE INTO citations VALUES (?, ?, ?, ?)
        """, (pn, cited, False, "forward"))
    for cited in patent_data.get("backward_citations", []):
        cursor.execute("""
            INSERT OR IGNORE INTO citations VALUES (?, ?, ?, ?)
        """, (pn, cited, False, "backward"))
    
    conn.commit()

def get_patents(assignee: str | None = None, limit: int | None = None) -> list[dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM patents"
    params = []
    if assignee:
        query += " WHERE assignee LIKE ?"
        params.append(f"%{assignee}%")
    if limit:
        query += f" LIMIT {limit}"
    
    cursor.execute(query, params)
    return [dict(row) for row in cursor.fetchall()]

def get_patent(patent_number: str) -> dict[str, Any] | None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patents WHERE patent_number = ?", (patent_number,))
    row = cursor.fetchone()
    return dict(row) if row else None

if __name__ == "__main__":
    conn = init_database()
    print("Database initialized")
    conn.close()