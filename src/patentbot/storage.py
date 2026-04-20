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
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database() -> sqlite3.Connection:
    """Initialize the database with required tables"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Patents table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patents (
            patent_number TEXT PRIMARY KEY,
            title TEXT,
            assignee TEXT,
            inventors TEXT,
            filing_date DATE,
            grant_date DATE,
            abstract TEXT,
            claims TEXT,
            cpc_codes TEXT,
            summary TEXT,
            key_problem TEXT,
            key_solution TEXT,
            tags TEXT,
            embedding BLOB,
            sources TEXT,
            fetched_at TIMESTAMP,
            summarized_at TIMESTAMP
        )
    """)
    
    # Citations table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS citations (
            citing_patent TEXT,
            cited_patent TEXT,
            family_cite BOOLEAN,
            direction TEXT,
            PRIMARY KEY (citing_patent, cited_patent, direction)
        )
    """)
    
    # Companies table
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
    """Save or update a patent record"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR REPLACE INTO patents (
            patent_number, title, assignee, inventors, filing_date, grant_date,
            abstract, claims, cpc_codes, sources, fetched_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        patent_data.get("patent_number"),
        patent_data.get("title"),
        patent_data.get("assignee"),
        json.dumps(patent_data.get("inventors", [])),
        patent_data.get("filing_date"),
        patent_data.get("grant_date"),
        patent_data.get("abstract"),
        patent_data.get("claims"),
        json.dumps(patent_data.get("cpc_codes", [])),
        json.dumps(patent_data.get("sources", [])),
        datetime.now().isoformat()
    ))
    
    conn.commit()

def save_citations(citations: list[dict[str, Any]]) -> None:
    """Save citation records"""
    conn = get_connection()
    cursor = conn.cursor()
    
    for cite in citations:
        cursor.execute("""
            INSERT OR IGNORE INTO citations (
                citing_patent, cited_patent, family_cite, direction
            ) VALUES (?, ?, ?, ?)
        """, (
            cite.get("citing_patent"),
            cite.get("cited_patent"),
            cite.get("family_cite", False),
            cite.get("direction")
        ))
    
    conn.commit()

def get_patents(assignee: str | None = None, limit: int | None = None) -> list[dict[str, Any]]:
    """Get patent records"""
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
    """Get a single patent"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM patents WHERE patent_number = ?", (patent_number,))
    row = cursor.fetchone()
    
    return dict(row) if row else None

def save_company(name: str, aliases: list[str]) -> None:
    """Save or update company record"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR REPLACE INTO companies (name, aliases, last_indexed)
        VALUES (?, ?, ?)
    """, (name, json.dumps(aliases), datetime.now().isoformat()))
    
    conn.commit()

if __name__ == "__main__":
    conn = init_database()
    print("Database initialized")
    conn.close()