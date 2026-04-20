"""
Patent discovery - scrape Google Patents search
"""
import asyncio
import re
from urllib.request import Request, urlopen
from urllib.parse import quote
from bs4 import BeautifulSoup

async def discover_patents(company: str, limit: int = 1000) -> list[str]:
    """Search Google Patents for company patents"""
    print(f"Searching Google Patents for: {company}")
    
    # Google Patents search URL
    query = quote(f"assignee:{company}")
    url = f"https://patents.google.com/?q={query}&num={limit}"
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    req = Request(url, headers=headers)
    
    try:
        webpage = urlopen(req, timeout=30).read()
        soup = BeautifulSoup(webpage, features="lxml")
        
        # Find patent numbers in search results
        patent_numbers = []
        
        # Look for patent-result-card or similar
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            # Match patterns like /patent/US7742806B2
            match = re.search(r'/patent/([A-Z]{2}\d+[A-Z]\d*[A-Z]?)', href)
            if match and match.group(1) not in patent_numbers:
                patent_numbers.append(match.group(1))
        
        print(f"Found {len(patent_numbers)} patents for {company}")
        return patent_numbers[:limit]
        
    except Exception as e:
        print(f"Error searching: {e}")
        return []

if __name__ == "__main__":
    import asyncio
    patents = asyncio.run(discover_patents("Medtronic"))
    print(f"Sample: {patents[:5]}")