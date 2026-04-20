"""
Embedding module - generate vector embeddings using Voyage AI
"""
import os
import json
import numpy as np
from typing import Dict, Any, List
import voyageai

async def embed_patent(
    patent_data: Dict[str, Any],
    client: voyageai.Client
) -> np.ndarray:
    """Generate embedding for a single patent"""
    # Combine title, summary, and CPC labels for embedding text
    title = patent_data.get("title", "")
    summary = patent_data.get("summary", "")
    cpc_codes = patent_data.get("cpc_codes", [])
    
    if isinstance(cpc_codes, str):
        cpc_codes = json.loads(cpc_codes)
    
    cpc_text = " ".join(cpc_codes)
    
    text = f"{title} {summary} {cpc_text}"
    
    try:
        result = client.embed(
            input=[text],
            model="voyage-3",
            dimensionality=1024
        )
        
        return np.array(result.embeddings[0], dtype=np.float32)
    except Exception as e:
        print(f"Error embedding patent {patent_data.get('patent_number')}: {e}")
        return np.zeros(1024, dtype=np.float32)

async def embed_patents(
    patent_data_list: List[Dict[str, Any]]
) -> List[np.ndarray]:
    """Generate embeddings for multiple patents"""
    api_key = os.getenv("VOYAGE_API_KEY")
    if not api_key:
        raise ValueError("VOYAGE_API_KEY not set")
    
    client = voyageai.Client(api_key=api_key)
    
    embeddings = []
    
    # Voyage has rate limits, batch if needed
    for patent_data in patent_data_list:
        embedding = await embed_patent(patent_data, client)
        embeddings.append(embedding)
    
    return embeddings

def save_embedding(patent_number: str, embedding: np.ndarray) -> None:
    """Save embedding to database"""
    from .storage import get_connection
    import sqlite3
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE patents SET embedding = ? WHERE patent_number = ?
    """, (embedding.tobytes(), patent_number))
    
    conn.commit()

def load_embedding(patent_number: str) -> np.ndarray:
    """Load embedding from database"""
    from .storage import get_connection
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT embedding FROM patents WHERE patent_number = ?", (patent_number,))
    row = cursor.fetchone()
    
    if row and row[0]:
        return np.frombuffer(row[0], dtype=np.float32)
    
    return np.zeros(1024, dtype=np.float32)

if __name__ == "__main__":
    async def test():
        test_patent = {
            "patent_number": "US7742806B2",
            "title": "Cardiac rhythm management device",
            "summary": "A device for managing cardiac rhythm...",
            "cpc_codes": ["A61N1/36"]
        }
        # Would need API key to test
        print("Embedding module loaded")
    
    import asyncio
    asyncio.run(test())