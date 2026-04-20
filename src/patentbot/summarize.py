"""
Summarization module - generate patent summaries using OpenRouter
"""
import os
import json
from typing import Any
from openrouter import OpenRouter

def summarize_patent(patent_data: dict[str, Any], client: OpenRouter) -> dict[str, Any]:
    """Generate summary for a single patent using OpenRouter"""
    pn = patent_data.get("patent_number", "")
    backward = patent_data.get("backward_citations", [])[:5] if patent_data.get("backward_citations") else []
    
    prompt = f"""Summarize this patent in ~100 words. Then extract:
- key_problem: one sentence on what problem it solves
- key_solution: one sentence on the technical mechanism
- tags: 3-6 short technical labels

Return JSON only. Do not speculate.

Patent: {pn}
Backward citations (prior art): {backward}"""

    try:
        response = client.chat.send(
            model="anthropic/claude-3-haiku",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        print(f"Error summarizing {pn}: {e}")
        return {}

def summarize_patents(patent_data_list: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Summarize multiple patents"""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not set")
    
    client = OpenRouter(api_key=api_key)
    
    summaries = []
    for pd in patent_data_list:
        result = summarize_patent(pd, client)
        summaries.append(result)
    
    return summaries

if __name__ == "__main__":
    from src.patentbot.storage import get_patent
    patent = get_patent("US7742806B2")
    result = summarize_patents([patent])
    print(result)