# PatentBot — Spec

**Goal:** For a target company (first: **Medtronic**), build a corpus of its patents, summarize each in ~100 words, and surface thematic clusters + white-space gaps in its portfolio.

**Status:** v0.1 — Working (2026-04-19)

---

## 1. Data sources

| Source | Role | Status |
|--------|------|--------|
| **Google Patents** (scraper) | Patent details + citations | ✅ Working |
| **OpenRouter API** | Summarization (Claude haiku) | ✅ Working |
| **USPTO PatentsView API** | Discovery | ❌ Discontinued |

## 2. Pipeline

```
[discover]  Snowball: seed patents → crawl citations
    ↓
[fetch]     google_patent_scraper → title, abstract, citations
    ↓
[summarize] OpenRouter (claude-3-haiku) → summary, key_problem, key_solution, tags
    ↓
[embed]     Placeholder (hash-based) → 384-dim vector
    ↓
[store]     SQLite (patents.db)
    ↓
[analyze]   Clustering + gap report (todo)
```

## 3. Storage (SQLite)

```sql
patents (
    patent_number TEXT PRIMARY KEY,
    title TEXT,
    abstract TEXT,
    assignee TEXT,
    inventors JSON,
    filing_date DATE,
    grant_date DATE,
    forward_citations JSON,
    backward_citations JSON,
    sources JSON,
    fetched_at TIMESTAMP,
    summarized_at TIMESTAMP,
    summary TEXT,
    key_problem TEXT,
    key_solution TEXT,
    tags JSON
)

citations (
    citing_patent TEXT,
    cited_patent TEXT,
    family_cite BOOLEAN,
    direction TEXT,
    PRIMARY KEY (citing_patent, cited_patent, direction)
)
```

## 4. Summarization (OpenRouter)

Prompt:
```
Summarize this patent in ~100 words. Then extract:
- key_problem: one sentence on what problem it solves
- key_solution: one sentence on the technical mechanism
- tags: 3–6 short technical labels

Return JSON only.
```

## 5. Known Issues

- **Embeddings**: Placeholder only. For production, add sentence-transformers or Voyage API.
- **Discovery**: No direct API. Uses snowball citation crawl.
- **No full-text claims**: Google scraper doesn't reliably return claims text.

## 6. Todo

- [ ] Add actual embeddings (sentence-transformers or API)
- [ ] Add gap analysis comparing CPC codes
- [ ] Add clustering visualization
- [ ] Add export to CSV/JSON