# PatentBot

A system for building patent corpora, summarizing patents, and identifying thematic clusters and white-space gaps in company patent portfolios.

## Features

- **Patent Discovery**: Fetch patents by company from USPTO PatentsView API
- **Multi-source Data**: Combine USPTO data with Google Patents citation graphs
- **AI Summarization**: Generate ~100-word summaries using Claude haiku-4.5
- **Vector Embeddings**: Use Voyage voyage-3 for semantic embeddings
- **Gap Analysis**: Identify thematic clusters and white-space opportunities
- **SQLite Storage**: Persistent storage with checkpointing and idempotent operations

## First Target: Medtronic

The initial implementation focuses on building a comprehensive patent corpus for Medtronic.

See [SPEC.md](SPEC.md) for detailed specifications.