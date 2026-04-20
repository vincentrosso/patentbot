"""
Main pipeline for PatentBot
"""
import asyncio
import json
from typing import Any
from .discovery import discover_patents
from .fetch import fetch_patent_details
from .storage import init_database, save_patent, get_patents

async def run_pipeline(company: str, args: Any) -> None:
    """Run the complete patent pipeline"""
    print(f"Starting PatentBot pipeline for {company}")
    
    # Initialize database
    db = init_database()
    
    # Check for manual patent list
    manual_patents = getattr(args, 'patents', None) or []
    
    if not any([args.discover_only, args.fetch_only, args.summarize_only, args.analyze_only]):
        print("Running full pipeline...")
        patent_numbers = await discover_patents(company) or manual_patents
        if patent_numbers:
            results = await fetch_patent_details(patent_numbers)
            for r in results:
                save_patent(r)
            print(f"Saved {len(results)} patents to database")
        print("Pipeline completed!")
    elif args.discover_only:
        print("Running discovery only...")
        patent_numbers = await discover_patents(company)
        print(f"Discovered {len(patent_numbers)} patents")
    elif args.fetch_only:
        print("Running fetch only...")
        patent_numbers = manual_patents
        if patent_numbers:
            results = await fetch_patent_details(patent_numbers)
            for r in results:
                save_patent(r)
            print(f"Fetched and saved {len(results)} patents")
        else:
            print("No patents to fetch (use --patents)")
    elif args.summarize_only:
        print("Running summarize only...")
        patents = get_patents(company)
        print(f"Found {len(patents)} patents in DB for {company}")
    elif args.analyze_only:
        print("Running analyze only...")
        patents = get_patents(company)
        print(f"Analyzing {len(patents)} patents")
    else:
        print("Unknown mode")

if __name__ == "__main__":
    asyncio.run(run_pipeline("Medtronic", type('Args', (), {
        'discover_only': False,
        'fetch_only': False,
        'summarize_only': False,
        'analyze_only': False,
        'patents': []
    })()))