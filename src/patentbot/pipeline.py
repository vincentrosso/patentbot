"""
Main pipeline for PatentBot
"""
import asyncio
from typing import Dict, Any
from .discovery import discover_patents
from .fetch import fetch_patent_details
from .storage import init_database

async def run_pipeline(company: str, args: Any) -> None:
    """Run the complete patent pipeline"""
    print(f"Starting PatentBot pipeline for {company}")
    
    # Initialize database
    db = init_database()
    
    # Check for manual patent list
    manual_patents = getattr(args, 'patents', None) or []
    
    if not any([args.discover_only, args.fetch_only, args.summarize_only, args.analyze_only]):
        # Run full pipeline
        print("Running full pipeline...")
        patent_numbers = await discover_patents(company) or manual_patents
        if patent_numbers:
            await fetch_patent_details(patent_numbers)
        print("Pipeline completed!")
    elif args.discover_only:
        print("Running discovery only...")
        patent_numbers = await discover_patents(company)
        print(f"Discovered {len(patent_numbers)} patents")
    elif args.fetch_only:
        print("Running fetch only...")
        patent_numbers = manual_patents
        if patent_numbers:
            await fetch_patent_details(patent_numbers)
        else:
            print("No patents to fetch (use --patents flag)")
    else:
        print("Specific mode selected - not yet implemented")

if __name__ == "__main__":
    asyncio.run(run_pipeline("Medtronic", type('Args', (), {
        'discover_only': False,
        'fetch_only': False,
        'summarize_only': False,
        'analyze_only': False
    })()))