"""
Patent fetch module - get details from USPTO and Google Patents
"""
import os
import asyncio
import aiohttp
from typing import List, Dict, Any, Tuple
from concurrent.futures import ThreadPoolExecutor

async def fetch_uspto_details(patent_number: str, session: aiohttp.ClientSession) -> Dict[str, Any]:
    """Fetch patent details from USPTO PatentsView API"""
    api_key = os.getenv("USPTO_API_KEY")
    if not api_key:
        raise ValueError("USPTO_API_KEY not set")

    url = "https://search.patentsview.org/api/v1/patent"
    
    query = {
        "q": {"patent_number": patent_number},
        "f": [
            "patent_number", "title", "assignee", "inventor",
            "filing_date", "grant_date", "abstract",
            "claims", "cpc_code"
        ]
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": api_key
    }

    try:
        async with session.post(url, json=query, headers=headers) as response:
            if response.status != 200:
                return {}
            
            data = await response.json()
            patents = data.get("patents", [])
            
            if not patents:
                return {}
            
            patent = patents[0]
            
            return {
                "patent_number": patent.get("patent_number"),
                "title": patent.get("title"),
                "assignee": patent.get("assignee", [{}])[0].get("assignee_organization") if patent.get("assignee") else None,
                "inventors": [inv.get("inventor_name") for inv in patent.get("inventor", [])],
                "filing_date": patent.get("filing_date"),
                "grant_date": patent.get("grant_date"),
                "abstract": patent.get("abstract"),
                "claims": patent.get("claims", [{}])[0].get("claim_text") if patent.get("claims") else None,
                "cpc_codes": [cpc.get("cpc_code") for cpc in patent.get("cpc_subgroup", [])],
                "source": "uspto"
            }
    except Exception as e:
        print(f"Error fetching USPTO details for {patent_number}: {e}")
        return {}

async def fetch_google_details(patent_number: str) -> Dict[str, Any]:
    """Fetch patent details from Google Patents using scraper"""
    try:
        from google_patent_scraper import scraper_helper, patents_scraper
        
        scraper = patents_scraper()
        result = scraper.single_patent_scraper(patent_number)
        
        if result.get("error"):
            return {}
        
        return {
            "forward_citations": result.get("forward_citation", []),
            "backward_citations": result.get("backward_citation", []),
            "family_citations": result.get("family_citation", []),
            "source": "google"
        }
    except Exception as e:
        print(f"Error fetching Google details for {patent_number}: {e}")
        return {}

async def fetch_patent_details(patent_numbers: List[str]) -> List[Dict[str, Any]]:
    """Fetch details for multiple patents concurrently"""
    results = []
    semaphore = asyncio.Semaphore(10)  # Limit concurrent requests
    
    async def fetch_with_semaphore(patent_number: str) -> Tuple[str, Dict[str, Any], Dict[str, Any]]:
        async with semaphore:
            async with aiohttp.ClientSession() as session:
                # Run USPTO and Google fetches concurrently
                uspto_task = fetch_uspto_details(patent_number, session)
                google_task = fetch_google_details(patent_number)
                
                uspto_data, google_data = await asyncio.gather(uspto_task, google_task)
                
                # Merge results
                merged = {**uspto_data}
                if google_data:
                    merged["forward_citations"] = google_data.get("forward_citations", [])
                    merged["backward_citations"] = google_data.get("backward_citations", [])
                    merged["family_citations"] = google_data.get("family_citations", [])
                    merged["sources"] = [s for s in ["uspto" if uspto_data else None, "google" if google_data else None] if s]
                
                return patent_number, uspto_data, google_data
    
    tasks = [fetch_with_semaphore(pn) for pn in patent_numbers]
    
    for task in asyncio.as_completed(tasks):
        pn, uspto, google = await task
        results.append({"patent_number": pn, "uspto": uspto, "google": google})
        
    return results

if __name__ == "__main__":
    asyncio.run(fetch_patent_details(["US7742806B2"]))