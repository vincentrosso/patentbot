"""
Patent discovery module - find patents by company
"""
import os
import asyncio
import aiohttp
from typing import List

async def discover_patents(company: str) -> List[str]:
    """Discover patents for a given company using USPTO PatentsView API"""
    api_key = os.getenv("USPTO_API_KEY")
    if not api_key:
        raise ValueError("USPTO_API_KEY environment variable not set")
    
    # USPTO PatentsView API endpoint
    url = "https://search.patentsview.org/api/v1/patent"
    
    # Query for patents assigned to the company
    query = {
        "q": {"assignee": company},
        "f": ["patent_number", "title", "assignee", "filing_date", "grant_date"],
        "o": {"per_page": 1000}  # Maximum per page
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": api_key
    }
    
    patent_numbers = []
    page = 1
    
    async with aiohttp.ClientSession() as session:
        while True:
            query["o"]["page"] = page
            
            async with session.post(url, json=query, headers=headers) as response:
                if response.status != 200:
                    print(f"Error: HTTP {response.status}")
                    break
                    
                data = await response.json()
                patents = data.get("patents", [])
                
                if not patents:
                    break
                    
                for patent in patents:
                    patent_numbers.append(patent["patent_number"])
                
                print(f"Page {page}: Found {len(patents)} patents")
                
                # Check if we have more pages
                if len(patents) < query["o"]["per_page"]:
                    break
                    
                page += 1
                
                # Respect rate limiting
                await asyncio.sleep(60 / 45)  # 45 requests per minute
    
    print(f"Total patents discovered: {len(patent_numbers)}")
    return patent_numbers

if __name__ == "__main__":
    async def test_discovery():
        patents = await discover_patents("Medtronic")
        print(f"Sample patents: {patents[:5]}")
    
    asyncio.run(test_discovery())