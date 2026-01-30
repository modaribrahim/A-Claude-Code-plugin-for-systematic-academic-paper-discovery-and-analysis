# Architecture Documentation

## System Overview

Research Companion is a Claude Code plugin that provides systematic academic paper discovery and analysis through a two-stage workflow. The system combines multi-source search, citation network analysis, and statistical tools to deliver comprehensive literature reviews with full traceability.

## Design Principles

- **Generic**: No hardcoded domains - works across all research fields
- **Traceable**: Every claim cites specific papers with numbered references
- **Session-based**: Each search creates isolated, timestamped folders
- **Extensible**: Easy to add new data sources and analysis methods
- **Domain-agnostic**: Scripts and workflows apply to any research topic

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Claude Code Interface                    │
│                  (User asks for papers)                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Skill: searching-ml-papers               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Stage 1: Paper Discovery                              │  │
│  │  • AskUserQuestions (4 questions)                    │  │
│  │  • Create Session (timestamped folder)               │  │
│  │  • Multi-Source Search (3 APIs)                      │  │
│  │  • Citation Filtering                                │  │
│  │  • Deduplication                                     │  │
│  │  • Citation Expansion (optional)                     │  │
│  │  • User Accept/Refine/Extend                          │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Session Data
                         │ (JSON files)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Skill: analyzing-papers                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Stage 2: Paper Analysis                              │  │
│  │  • Select Input (which session?)                     │  │
│  │  • Validate Session                                  │  │
│  │  • Strategy Selection (Quick vs Comprehensive)       │  │
│  │  • Hybrid Analysis:                                  │  │
│  │    - Temporal Data Extraction                        │  │
│  │    - Graph Algorithms (PageRank, betweenness)        │  │
│  │    - Statistical Tools (distributions, correlations)  │  │
│  │    - LLM Strategic Reading (top papers)              │  │
│  │  • Report Generation (full traceability)             │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
                    Markdown Report
                 (with numbered citations)
```

## Core Components

### 1. Session Management

**Location**: `skills/searching-ml-papers/tools/scripts/create_session.py`

**Purpose**: Creates isolated, timestamped folders for each search

**Data Structure**:
```
session_YYYYMMDD_HHMMSS_topic/
├── metadata.json           # Search parameters, user preferences
├── search_results.json     # Raw results from all sources
├── filtered.json           # After citation filtering
├── deduplicated.json       # Final paper collection
└── summary.json            # Statistics, top papers
```

**Key Features**:
- Unique timestamps prevent data loss
- Metadata tracks search parameters
- Sessions can be merged (extend) or refined
- JSON format for LLM processing

### 2. Multi-Source Search System

**Location**: `skills/searching-ml-papers/tools/`

#### 2.1 API Clients

| Client | File | Purpose |
|--------|------|---------|
| arXiv | `arxiv_client.py` | Preprints, CS/physics/math |
| Semantic Scholar | `semantic_scholar_client.py` | Comprehensive metadata, citations |
| OpenAlex | `openalex_client.py` | Cross-disciplinary coverage |

**Design Pattern**: All clients follow the same interface:
```python
search(query, year_from, year_to, fields_of_study, venue, max_results)
→ List[Dict]  # Unified paper format
```

#### 2.2 Unified Paper Format

```json
{
  "id": "arxiv:2301.00001",
  "title": "Paper Title",
  "authors": ["Author 1", "Author 2"],
  "year": 2023,
  "abstract": "Full text...",
  "venue": "arXiv",
  "citationCount": 42,
  "url": "https://arxiv.org/abs/2301.00001",
  "pdfUrl": "https://arxiv.org/pdf/2301.00001.pdf"
}
```

### 3. Data Processing Pipeline

#### 3.1 Citation Filtering

**Location**: `skills/searching-ml-papers/tools/scripts/filter_citations.py`

**Purpose**: Rank papers by impact (citation count)

**Logic**:
- Extract `citationCount` from each paper
- Filter by user-specified minimum
- Sort by citations (descending)
- Keep top N papers

#### 3.2 Deduplication

**Location**: `skills/searching-ml-papers/tools/scripts/deduplicate_sources.py`

**Purpose**: Remove duplicate papers across sources

**Strategy**: Multi-stage deduplication
1. **DOI** (exact match)
2. **Title** (exact match, case-insensitive)
3. **Title + Year** (fuzzy match)
4. **Authors + Year** (partial match)

**Algorithm**:
- Build signature for each paper
- Use hash-based lookup (O(n) complexity)
- Keep first occurrence (prioritize Semantic Scholar > arXiv > OpenAlex)

#### 3.3 Citation Expansion

**Location**: `skills/searching-ml-papers/tools/scripts/citation_expand.py`

**Purpose**: Find papers that cite seed papers

**Use Case**: Comprehensive searches need forward citations

**Method**:
- For each high-impact paper (top 20)
- Query Semantic Scholar for "citing papers"
- Merge with existing collection
- Re-run deduplication

### 4. Analysis System

**Location**: `skills/analyzing-papers/tools/`

#### 4.1 Input Selection

**Script**: `select_input.py`

**Purpose**: Choose which session to analyze

**Features**:
- List all available sessions
- Show session metadata (topic, paper count, date)
- Validate session has required files

#### 4.2 Network Analysis

**Script**: `build_network.py`

**Purpose**: Build citation network structure

**Output Format**:
```json
{
  "nodes": [
    {
      "id": "paper1",
      "title": "...",
      "citations": 42,
      "authors": ["..."],
      "year": 2023
    }
  ],
  "edges": [
    {
      "from": "paper1",
      "to": "paper2",
      "type": "cites"
    }
  ],
  "stats": {
    "total_papers": 100,
    "total_citations": 1234,
    "avg_citations": 12.34
  }
}
```

**Script**: `graph_algorithms.py`

**Algorithms**:
- **PageRank**: Identify influential papers
- **Betweenness Centrality**: Find bridge papers
- **Community Detection**: Research clusters (Louvain method)

#### 4.3 Temporal Analysis

**Script**: `extract_temporal.py`

**Purpose**: Track trends over time

**Metrics**:
- Papers per year
- Citations per year
- Average citations (yearly)
- Growth rate

**Visualization**: Generates markdown tables and stats

#### 4.4 Statistical Analysis

**Script**: `statistical_tools.py`

**Purpose**: Quantitative analysis of collection

**Tests**:
- Distribution of citations (log-normal?)
- Correlation: citations vs year
- Top venues (conference/journal frequency)
- Author productivity

## Data Flow

### Search Workflow

```
User Query
    ↓
AskUserQuestions (4x)
    ↓
create_session.py → session_folder/
    ↓
multi_search.py
    ├→ arxiv_client.py ────┐
    ├→ semantic_scholar_client.py ─┼→ raw_results
    └→ openalex_client.py ──────┘
    ↓
filter_citations.py → filtered_results
    ↓
deduplicate_sources.py → deduplicated_results
    ↓
[if comprehensive]
    ↓
citation_expand.py → expanded_results
    ↓
AskUserQuestion (Accept/Refine/Extend)
    ↓
summarize_results.py → summary.json
```

### Analysis Workflow

```
User: "Analyze that session"
    ↓
select_input.py → session_folder/
    ↓
validate_session.py
    ↓
Check paper count
    ├─ ≤20 papers → Quick Strategy (LLM reads all)
    └─ >20 papers → Comprehensive Strategy
        ↓
        ├─ extract_temporal.py → temporal_data.json
        ├─ build_network.py → graph_data.json
        ├─ graph_algorithms.py → pagerank_results.json
        ├─ statistical_tools.py → stats.json
        └─ LLM reads top 10 papers (by PageRank)
    ↓
Generate Report → analysis.md
```

## Extension Points

### Adding a New Data Source

1. Create client: `skills/searching-ml-papers/tools/your_source_client.py`
2. Implement interface:
   ```python
   def search(query, year_from, year_to, fields, venue, max_results):
       # Query API
       # Transform to unified format
       return papers
   ```
3. Add to `multi_search.py`:
   ```python
   from your_source_client import search_source
   results = search_source(...)
   all_results.extend(results)
   ```

### Adding a New Analysis Method

1. Create script: `skills/analyzing-papers/tools/scripts/your_analysis.py`
2. Add to SKILL.md workflow
3. Example: keyword co-occurrence, author collaboration networks

### Adding Pre-commit Hooks

Edit `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/your-hook
    hooks:
      - id: your-hook
```

## Security Considerations

### API Keys

**Storage**: Environment variables (never in code)
- `SEMANTIC_SCHOLAR_API_KEY` (optional, for higher rate limits)
- `OPENALEX_EMAIL` (optional, for polite requests)

**Gitleaks**: Pre-commit hook prevents accidental commits

### Input Validation

All scripts validate:
- Date ranges (year_from ≤ year_to)
- Integer parameters (max-results, min-citations)
- File existence before processing

## Performance Optimization

### Caching

- API responses cached in `search_results.json`
- No redundant API calls during refinement
- Reuse session data during analysis

### Parallel Queries

API clients can run in parallel (not yet implemented):
```bash
# Future optimization
arxiv_client.py &  # Background
semantic_scholar_client.py &  # Background
openalex_client.py &  # Background
wait  # Collect all results
```

### Large Datasets

For 500+ papers:
- Don't read entire JSON into LLM context
- Use scripts to extract statistics
- LLM reads summaries, not raw data

## Testing Strategy

### Unit Tests

**Location**: `skills/*/tools/test_*.py`

**Coverage**:
- Import tests (dependencies available?)
- Script existence checks
- File structure validation

### Manual Testing

**Test Cases**:
- Quick search (20 papers)
- Comprehensive search (500+ papers)
- Refine existing session
- Extend session (merge)
- Analyze quick session
- Analyze comprehensive session

### Edge Cases

- No results found
- API rate limits
- Malformed API responses
- Missing session files
- Empty abstracts

## Dependencies

### Per-Skill Management

Each skill has its own `pyproject.toml`:
- `skills/searching-ml-papers/tools/pyproject.toml`
- `skills/analyzing-papers/tools/pyproject.toml`

**Benefits**:
- Isolated dependencies
- Can version skills independently
- Clear dependency boundaries

### Shared Dependencies

Both skills use:
- `requests>=2.32.0` (HTTP client)
- `numpy>=1.24.0` (numerical operations)

**searching-ml-papers only**:
- `arxiv>=2.4.0`
- `sentence-transformers>=2.2.0` (embeddings)
- `click>=8.0.0` (CLI)

## File Organization

### Session Data (Artifacts)

**Search Sessions**: `skills/searching-ml-papers/tools/artifacts/session_*/`
**Analysis Experiments**: `skills/analyzing-papers/tools/artifacts/experiment_*/`

**Lifecycle**:
- Created by user request
- Persist across sessions
- Can be deleted manually
- Not tracked by git (in .gitignore)

### Plugin Structure

```
. (repo root)
├── skills/                    # Plugin root (not .claude/)
│   ├── searching-ml-papers/
│   │   └── tools/
│   │       ├── scripts/       # Executable scripts
│   │       ├── *.py          # API clients
│   │       ├── utils/        # Utilities
│   │       ├── pyproject.toml
│   │       └── artifacts/     # Sessions
│   └── analyzing-papers/
│       └── tools/
├── hooks/                     # Plugin hooks
├── .claude-plugin/            # Plugin manifest
└── docs/                      # Documentation
```

## Known Limitations

1. **Citation Data**: APIs don't always return full reference lists
   - Workaround: Use citation counts as influence proxy
   - Future: Semantic Scholar "citations" endpoint

2. **Rate Limits**: Public APIs have limits
   - Workaround: Use API keys, implement delays
   - Future: Distributed search

3. **Coverage**: Some fields poorly represented
   - arXiv: Strong in CS/physics/math
   - OpenAlex: Broad but variable quality
   - Semantic Scholar: Best for computer science

## Future Improvements

### Short Term
- [ ] Add progress bars for long operations
- [ ] Implement parallel API queries
- [ ] Add more graph algorithms (community detection)
- [ ] Export to BibTeX, CSV

### Long Term
- [ ] Vector search (semantic similarity)
- [ ] Full-text PDF analysis
- [ ] Multi-modal (figures, tables)
- [ ] Citation network visualization
- [ ] Web UI for session management

## Related Systems

- [Connected Papers](https://www.connectedpapers.com/) - Citation network visualization
- [Semantic Scholar](https://www.semanticscholar.org/) - API source
- [OpenAlex](https://openalex.org/) - Open citation database
- [arXiv](https://arxiv.org/) - Preprint server

## References

- Claude Code Plugin Documentation: https://docs.claude.com/claude-code
- Semantic Scholar API: https://www.semanticscholar.org/product/api
- OpenAlex API: https://docs.openalex.org/
- arXiv API (via arxiv.py): https://github.com/lukasschwab/arxiv.py

---

**Document Version**: 1.0.0
**Last Updated**: 2026-01-30
**Maintainer**: Modar Ibrahim <ibmd7275@gmail.com>
