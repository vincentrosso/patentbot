# PatentBot — Spec

**Goal:** For a target company (first: **Medtronic**), build a corpus of its patents, summarize each in ~100 words, and surface thematic clusters + white-space gaps in its portfolio.

**Status:** Draft v0.1 — 2026-04-19

---

## 1. Data sources

Two sources, run **concurrently per patent** (not redundantly — they return different fields):

| Source | Role | Returns |
|---|---|---|
| **USPTO PatentsView API** (`https://search.patentsview.org/api/v1/`) | Primary — discovery + classification + full text | Patent list by assignee, CPC codes, abstract, claims, filing/grant dates, inventor, assignee |
| **`ryanlstevens/google_patent_scraper`** (PyPI: `google_patent_scraper`) | Secondary — citation graph + cross-check | Forward/backward citations (with/without family), abstract, inventor, assignee |

**Why both:** USPTO gives us classification (CPC codes — critical for gap analysis) and full claims; the Google scraper gives us the citation graph, which USPTO's free API surfaces awkwardly. Citations + CPC together are what let us compute gaps, not just a list.

**Rate limits:**
- USPTO PatentsView: 45 req/min (authenticated, free key).
- Google Patents: no official limit; scraper respects HTML — throttle to 1 req/sec, use retries + jitter to avoid bot-block.

## 2. Pipeline

```
[discover]  USPTO search: assignee="Medtronic" → patent_number[]
    ↓
[fetch]     per patent, in parallel (asyncio.gather):
              ├─ USPTO detail call   → abstract, claims, CPC codes
              └─ google_patent_scraper → citations, cross-check abstract
    ↓
[merge]     dedupe on patent_number; prefer USPTO fields; attach citations from scraper
    ↓
[summarize] Claude (haiku-4.5) → ~100-word summary, key_problem, key_solution, tags[]
    ↓
[embed]     Voyage voyage-3 → 1024-dim vector over (title + summary + CPC labels)
    ↓
[store]     SQLite (patents.db) — one file, queryable, diffable in git-ignore
    ↓
[analyze]   cluster + gap report (see §5)
```

Stages are idempotent and checkpointed — re-running only fetches missing work.

## 3. Storage schema (SQLite)

```sql
patents (
  patent_number TEXT PRIMARY KEY,  -- e.g. "US7742806B2"
  title TEXT,
  assignee TEXT,
  inventors JSON,
  filing_date DATE,
  grant_date DATE,
  abstract TEXT,
  claims TEXT,               -- full text, USPTO
  cpc_codes JSON,            -- ["A61N1/36", ...]
  summary TEXT,              -- Claude, ~100 words
  key_problem TEXT,          -- Claude
  key_solution TEXT,         -- Claude
  tags JSON,                 -- Claude, short labels
  embedding BLOB,            -- Voyage vector, float32
  sources JSON,              -- which sources succeeded: ["uspto","google"]
  fetched_at TIMESTAMP,
  summarized_at TIMESTAMP
)

citations (
  citing_patent TEXT,
  cited_patent TEXT,
  family_cite BOOLEAN,
  direction TEXT CHECK(direction IN ('forward','backward')),
  PRIMARY KEY (citing_patent, cited_patent, direction)
)

companies (
  name TEXT PRIMARY KEY,     -- "Medtronic"
  aliases JSON,              -- ["Medtronic, Inc.", "Medtronic plc", ...]
  last_indexed TIMESTAMP
)
```

## 4. Summarization

Per-patent prompt (Claude haiku-4.5, with prompt caching on the system prompt):

```
Summarize this patent in ~100 words. Then extract:
- key_problem: one sentence on what problem it solves
- key_solution: one sentence on the technical mechanism
- tags: 3–6 short technical labels (e.g. "closed-loop stimulation", "lead fixation")

Return JSON. Do not speculate beyond the text.

<patent>
Title: {title}
CPC: {cpc_codes}
Abstract: {abstract}
Claims: {first_3_claims}
```