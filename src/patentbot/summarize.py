"""
Summarization module - generate patent summaries using Claude
"""
import os
import json
import asyncio
from typing import Any
import anthropic

SYSTEM_PROMPT = """You are a patent analysis expert. Summarize patents concisely and extract key technical details.

Respond with valid JSON only. Do not add explanation or commentary outside the JSON.
Extract exactly these fields:
- summary: ~100 word summary of the patent
- key_problem: one sentence on what problem it solves
- key_solution: one sentence on the technical mechanism
- tags: 3-6 short technical labels (e.g. "closed-loop stimulation", "lead fixation")

Do not speculate beyond the text provided."""

async def summarize_patent(
    patent_data: Dict[str, Any],
    client: anthropic.AsyncAnthropic
) -> Dict[str, Any]:
    """Generate summary for a single patent"""
    title = patent_data.get("title", "")
    abstract = patent_data.get("abstract", "")
    cpc_codes = patent_data.get("cpc_codes", [])
    claims = patent_data.get("claims", "")
    
    # Get first 3 claims
    if claims:
        claims_list = claims.split("\n")[:3]
        first_claims = "\n".join(claims_list)
    else:
        first_claims = "N/A"

    prompt = f"""Summarize this patent in ~100 words. Then extract:
- key_problem: one sentence on what problem it solves
- key_solution: one sentence on the technical mechanism
- tags: 3–6 short technical labels (e.g. "closed-loop stimulation", "lead fixation")

Return JSON. Do not speculate beyond the text.

<patent>
Title: {title}
CPC: {cpc_codes}
Abstract: {abstract}
Claims: {first_claims}"""

    try:
        response = await client.messages.create(
            model="claude-haiku-4-2025-04-19",
            max_tokens=500,
            system=[{"type": "text", "text": SYSTEM_PROMPT}],
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Parse JSON from response
        content = response.content[0].text
        return json.loads(content)
    except Exception as e:
        print(f"Error summarizing patent {patent_data.get('patent_number')}: {e}")
        return {}

async def summarize_patents(
    patent_data_list: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Summarize multiple patents with rate limiting"""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set")
    
    client = anthropic.AsyncAnthropic(api_key=api_key)
    
    summaries = []
    # Rate limit: 5 requests per minute for haiku
    semaphore = asyncio.Semaphore(5)
    
    async def summarize_with_limit(pd: Dict[str, Any]) -> Dict[str, Any]:
        async with semaphore:
            result = await summarize_patent(pd, client)
            await asyncio.sleep(12)  # 5 req/min = 12 sec between requests
            return result
    
    tasks = [summarize_with_limit(pd) for pd in patent_data_list]
    
    for coro in asyncio.as_completed(tasks):
        summary = await coro
        summaries.append(summary)
    
    return summaries

if __name__ == "__main__":
    async def test():
        test_patent = {
            "patent_number": "US7742806B2",
            "title": "Cardiac rhythm management device with distributed sensing",
            "abstract": "A cardiac rhythm management device includes distributed sensing electrodes...",
            "cpc_codes": ["A61N1/36"],
            "claims": "1. A cardiac rhythm management device comprising..."
        }
        # Would need API key to test
        print("Summarization module loaded")
    
    asyncio.run(test())