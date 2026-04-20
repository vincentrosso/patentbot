"""
Summarization module - generate patent summaries using OpenRouter
"""
import os
import json
import asyncio
from typing import Any

async def summarize_patent(
    patent_data: dict[str, Any],
    client
) -> dict[str, Any]:
    """Generate summary for a single patent using OpenRouter"""
    title = patent_data.get("title") or ""
    abstract = patent_data.get("abstract") or ""
    cpc_codes = patent_data.get("cpc_codes", []) or []
    backward = patent_data.get("backward_citations", [])[:5] if patent_data.get("backward_citations") else []
    
    prompt = f"""Summarize this patent in ~100 words. Then extract:
- key_problem: one sentence on what problem it solves
- key_solution: one sentence on the technical mechanism
- tags: 3-6 short technical labels

Return JSON. Do not speculate.

<patent>
Title: {title}
Backward citations (prior art): {backward}
Abstract: {abstract}"""

    try:
        response = await client.chat.completions.create(
            model="anthropic/claude-3-haiku",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        print(f"Error summarizing {patent_data.get('patent_number')}: {e}")
        return {}

async def summarize_patents(
    patent_data_list: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Summarize multiple patents with rate limiting"""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not set")
    
    from openrouter import AsyncOpenRouter
    client = AsyncOpenRouter(api_key=api_key)
    
    summaries = []
    semaphore = asyncio.Semaphore(5)
    
    async def summarize_with_limit(pd: dict[str, Any]) -> dict[str, Any]:
        async with semaphore:
            result = await summarize_patent(pd, client)
            await asyncio.sleep(12)
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
            "backward_citations": ["US5092343A"]
        }
        print("Needs API key to test")
    
    asyncio.run(test())