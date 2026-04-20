# PatentBot

Patent corpus builder for analyzing company patent portfolios. Fetches patents, summarizes with AI, and identifies thematic clusters + white-space gaps.

## Quick Start

```bash
# Clone and setup
git clone https://github.com/vincentrosso/patentbot.git
cd patentbot

# Install dependencies
pip install -r requirements.txt

# Copy env template and add API key
cp .env.example .env
# Edit .env and add: OPENROUTER_API_KEY=your_key
```

## Usage

### Fetch Patents (from Google Patents)

```bash
PYTHONPATH=src python -m patentbot Medtronic --fetch-only --patents US7742806B2 US3955174A
```

### Discovery (snowball via citations)

```bash
PYTHONPATH=src python -m patentbot Medtronic --discover-only
```

### Summarize Patents

```python
from src.patentbot.summarize import summarize_patents
from src.patentbot.storage import get_patent

patent = get_patent("US7742806B2")
summary = summarize_patents([patent])
print(summary[0]["summary"])
```

### Embeddings

```python
from src.patentbot.embed import embed_patent

vec = embed_patent("Cardiac pacemaker device")  # 384-dim vector
```

### Database

```python
from src.patentbot.storage import get_patents, get_patent, init_database

init_database()  # Create tables
patents = get_patents()  # All patents
patents = get_patents("Medtronic")  # By assignee
patent = get_patent("US7742806B2")  # By number
```

## API Keys

Get a free key at https://openrouter.ai:

```
OPENROUTER_API_KEY=sk-or-v1-...
```

Add to `.env` file.

## Project Structure

```
patentbot/
├── src/patentbot/
│   ├── discovery.py    # Snowball discovery via citations
│   ├── fetch.py       # Google Patents scraper
│   ├── storage.py     # SQLite database
│   ├── summarize.py  # OpenRouter AI summarization
│   ├── embed.py      # Text embeddings
│   ├── analyze.py    # Clustering + gap analysis
│   └── pipeline.py   # Main pipeline
├── patents.db        # SQLite database (created on first run)
├── requirements.txt
├── SPEC.md          # Full specification
└── .env.example    # Env template
```

## Database Schema

```sql
-- Patents table
patents (
    patent_number TEXT PRIMARY KEY,
    title TEXT,
    abstract TEXT,
    assignee TEXT,
    inventors TEXT,        -- JSON array
    filing_date DATE,
    grant_date DATE,
    forward_citations TEXT,  -- JSON array
    backward_citations TEXT,-- JSON array
    sources TEXT,           -- JSON array
    fetched_at TIMESTAMP,
    summarized_at TIMESTAMP,
    summary TEXT,
    key_problem TEXT,
    key_solution TEXT,
    tags TEXT              -- JSON array
)

-- Citations table
citations (
    citing_patent TEXT,
    cited_patent TEXT,
    family_cite BOOLEAN,
    direction TEXT,         -- 'forward' or 'backward'
    PRIMARY KEY (citing_patent, cited_patent, direction)
)

-- Companies table
companies (
    name TEXT PRIMARY KEY,
    aliases TEXT,           -- JSON array
    last_indexed TIMESTAMP
)
```

## Current Status

| Feature | Status |
|---------|--------|
| Fetch from Google Patents | ✅ Working |
| Snowball Discovery | ✅ Working |
| OpenRouter Summarization | ✅ Working |
| Embeddings | ⚠️ Placeholder (hash-based) |
| USPTO Discovery | ❌ API discontinued |

## Notes

- **Embeddings**: Current implementation is placeholder (hash-based). For production, add sentence-transformers or API key for Voyage.
- **Discovery**: Uses snowball method - starts with seed patents, crawls forward/backward citations. Pre-seeded with Medtronic cardiac patents.
- **Rate limiting**: OpenRouter has free tier. Google Patents scraper respects 1 req/sec.

## License

MIT