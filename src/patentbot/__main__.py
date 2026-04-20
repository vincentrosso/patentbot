#!/usr/bin/env python3
"""
PatentBot main entry point
"""
import asyncio
import argparse
from .pipeline import run_pipeline

def main():
    parser = argparse.ArgumentParser(description="PatentBot - Patent corpus builder and analyzer")
    parser.add_argument("company", help="Company name to analyze")
    parser.add_argument("--discover-only", action="store_true", help="Only discover patents, don't fetch details")
    parser.add_argument("--fetch-only", action="store_true", help="Only fetch patent details")
    parser.add_argument("--summarize-only", action="store_true", help="Only summarize patents")
    parser.add_argument("--analyze-only", action="store_true", help="Only run analysis")
    parser.add_argument("--patents", nargs="+", help="Manual list of patent numbers to process")
    
    args = parser.parse_args()
    
    asyncio.run(run_pipeline(args.company, args))

if __name__ == "__main__":
    main()