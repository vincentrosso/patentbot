"""
Patent fetch module - get details from Google Patents
"""
import asyncio
import json
from typing import Any
from concurrent.futures import ThreadPoolExecutor

def fetch_patent_data(patent_number: str) -> dict[str, Any]:
    """Fetch patent details from Google Patents"""
    from google_patent_scraper import scraper_class
    
    scraper = scraper_class()
    status, soup, url = scraper.request_single_patent(patent_number)
    
    if status != 'Success':
        return {"patent_number": patent_number, "error": status}
    
    raw = scraper.get_scraped_data(soup, patent_number, url)
    
    def parse_json_field(val):
        if isinstance(val, str):
            try:
                return json.loads(val)
            except:
                return val
        return val
    
    inventors = parse_json_field(raw.get("inventor_name", []))
    if isinstance(inventors, list):
        inventors = [i.get("inventor_name") for i in inventors if isinstance(i, dict)]
    
    assignee_orig = parse_json_field(raw.get("assignee_name_orig", []))
    if isinstance(assignee_orig, list) and assignee_orig:
        assignee_orig = assignee_orig[0].get("assignee_name")
    
    forward_cites = parse_json_field(raw.get("forward_cite_no_family", []))
    forward_family = parse_json_field(raw.get("forward_cite_yes_family", []))
    backward_cites = parse_json_field(raw.get("backward_cite_no_family", []))
    backward_family = parse_json_field(raw.get("backward_cite_yes_family", []))
    
    return {
        "patent_number": patent_number,
        "assignee": assignee_orig if assignee_orig else None,
        "inventors": inventors,
        "grant_date": raw.get("grant_date"),
        "filing_date": raw.get("filing_date"),
        "priority_date": raw.get("priority_date"),
        "pub_date": raw.get("pub_date"),
        "forward_citations": [c.get("patent_number") for c in forward_cites] if isinstance(forward_cites, list) else [],
        "forward_family_citations": [c.get("patent_number") for c in forward_family] if isinstance(forward_family, list) else [],
        "backward_citations": [c.get("patent_number") for c in backward_cites] if isinstance(backward_cites, list) else [],
        "backward_family_citations": [c.get("patent_number") for c in backward_family] if isinstance(backward_family, list) else [],
        "sources": ["google"]
    }

async def fetch_patent_details(patent_numbers: list[str]) -> list[dict[str, Any]]:
    """Fetch details for multiple patents concurrently"""
    loop = asyncio.get_event_loop()
    results = []
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            loop.run_in_executor(executor, fetch_patent_data, pn)
            for pn in patent_numbers
        ]
        
        for future in asyncio.as_completed(futures):
            result = await future
            results.append(result)
            print(f"Fetched: {result.get('patent_number')}")
    
    return results

if __name__ == "__main__":
    import asyncio
    result = fetch_patent_data("US7742806B2")
    print(f"Sample: {result}")