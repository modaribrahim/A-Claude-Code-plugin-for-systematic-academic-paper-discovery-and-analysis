# Research Companion for Claude Code

**Systematic academic paper discovery and analysis with full citation traceability**

[![Status: Under Development](https://img.shields.io/badge/Status-Under%20Development-yellow.svg)](https://github.com/modaribrahim/A-Claude-Code-plugin-for-systematic-academic-paper-discovery-and-analysis)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Claude Code Plugin](https://img.shields.io/badge/Claude%20Code-Plugin-purple.svg)](https://docs.claude.com/claude-code)

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/badge/uv-Package%20Manager-green.svg)](https://docs.astral.sh/uv/)
[![Ruff](https://img.shields.io/badge/Ruff-Enabled-red.svg)](https://docs.astral.sh/ruff/)

---

<p align="center">
  <img src="assets/logo.png" alt="Research Companion Logo" width="180" height="150">
</p>

<pre align="center">
▛▀▖                  ▌   ▞▀▖                ▗
▙▄▘▞▀▖▞▀▘▞▀▖▝▀▖▙▀▖▞▀▖▛▀▖ ▌  ▞▀▖▛▚▀▖▛▀▖▝▀▖▛▀▖▄ ▞▀▖▛▀▖
▌▚ ▛▀ ▝▀▖▛▀ ▞▀▌▌  ▌ ▖▌ ▌ ▌ ▖▌ ▌▌▐ ▌▙▄▘▞▀▌▌ ▌▐ ▌ ▌▌ ▌
▘ ▘▝▀▘▀▀ ▝▀▘▝▀▘▘  ▝▀ ▘ ▘ ▝▀ ▝▀ ▘▝ ▘▌  ▝▀▘▘ ▘▀▘▝▀ ▘ ▘
</pre>

<p align="center">
  <b>Search</b> • <b>Analyze</b> • <b>Cite</b>
</p>

---

## What It Does

Search across arXiv, Semantic Scholar, and OpenAlex → Analyze citation networks → Generate traceable reports with **every claim cited**.

**Perfect for**:
- Literature reviews
- Survey papers
- State-of-the-art research
- Finding influential papers
- Tracking research trends

---

## Quick Start

### 1. Install Plugin

```bash
% claude
> /plugin marketplace add modaribrahim/A-Claude-Code-plugin-for-systematic-academic-paper-discovery-and-analysis
  ⎿  Successfully added marketplace: research-companion

> /plugin install research-companion@research-companion
  ⎿  ✓ Installed research-companion. Restart Claude Code.
```

### 2. Use It

Simply ask Claude to find papers:

```
"Do a comprehensive search on quantum machine learning"
```

Claude will ask 4 questions, then search, filter, and present results.

Then analyze:

```
"Analyze that session"
```

You'll get a detailed report with:
- Executive summary (cited)
- Influential papers (PageRank)
- Temporal trends
- Research gaps
- Full paper list (Appendix A)

---

## Key Features

### 🔍 Multi-Source Search
- **arXiv** - Latest preprints (CS/physics/math)
- **Semantic Scholar** - Comprehensive metadata, citations
- **OpenAlex** - Cross-disciplinary coverage

### 📊 Two Search Modes
- **Quick** - 20 papers in 10 seconds
- **Comprehensive** - 500+ papers with citation expansion

### 🌐 Citation Network Analysis
- PageRank (influential papers)
- Betweenness centrality (bridge papers)
- Community detection (research clusters)

### 📈 Statistical Analysis
- Citation distributions
- Temporal trends (year-by-year)
- Venue analysis
- Author productivity

### 🎯 Full Traceability
- Every claim cites specific papers
- Numbered references
- Direct links to papers

### 🔄 Session Management
- Each search = unique folder (no data loss)
- Refine or extend searches
- Re-analyze anytime

---

## Workflow

```
┌─────────────────┐
│ Ask for papers  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│ 1. Search (Multi-source)               │
│    ├→ arXiv + Semantic Scholar + OpenAlex
│    ├→ Filter by citations               │
│    ├→ Remove duplicates                │
│    └→ Expand citations (optional)      │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│ 2. Accept / Refine / Extend            │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│ 3. Analyze                              │
│    ├→ Citation network (PageRank)      │
│    ├→ Temporal trends                  │
│    ├→ Statistical analysis             │
│    └→ LLM strategic reading             │
└────────┬────────────────────────────────┘
         │
         ▼
    Traceable Report
```

**See [docs/architecture.md](docs/architecture.md) for detailed system design.**

---

## Installation

### Prerequisites

- [Claude Code](https://docs.claude.com/claude-code) installed
- Python 3.9+
- [uv](https://docs.astral.sh/uv/) (package manager)

### Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# or: pip install uv
```

### Install Plugin

```bash
claude
> /plugin marketplace add modaribrahim/A-Claude-Code-plugin-for-systematic-academic-paper-discovery-and-analysis
> /plugin install research-companion@research-companion
```

Dependencies install automatically via `uv sync`.

### Manual Setup (Optional)

If dependencies don't install automatically:

```bash
cd skills/searching-ml-papers/tools && uv sync
cd ../analyzing-papers/tools && uv sync
```

---

## Usage Examples

### Example 1: Quick Literature Review

```
"Find papers on transformer architectures in computer vision"
```

→ Claude asks questions
→ Searches 3 sources
→ Returns top 20 papers (filtered by citations)
→ Session saved for analysis

### Example 2: Comprehensive Survey

```
"Do a comprehensive search on federated learning from 2020-2024"
```

→ Searches 500+ papers
→ Citation expansion (finds papers citing top results)
→ De-duplicates across sources
→ Saves to session

```
"Analyze that session"
```

→ Citation network analysis
→ Temporal trends
→ Statistical distributions
→ Generates 20-page report

### Example 3: Refine Search

```
"Refine that search to focus on healthcare applications"
```

→ Updates session with new query
→ Merges with existing results
→ No data loss

---

## Output

### Search Sessions

Located in: `skills/searching-ml-papers/tools/artifacts/session_*/`

```
session_20250130_143026_federated_learning/
├── metadata.json              # Search parameters
├── search_results.json        # Raw results
├── deduplicated.json          # Final collection
└── summary.json               # Top papers, stats
```

### Analysis Reports

Generated in: `skills/analyzing-papers/tools/artifacts/experiment_*/`

**Report includes**:
- **Executive Summary** (3-5 key insights with citations)
- **Research Landscape** (methods, datasets, metrics)
- **Citation Network Insights** (influential papers, clusters)
- **Temporal Trends** (evolution over time)
- **Statistical Analysis** (distributions, correlations)
- **Research Gaps** (opportunities)
- **Appendix A** (all papers with details)

---

## Advanced Usage

### Optional API Keys

**Semantic Scholar** (higher rate limits):
```bash
export SEMANTIC_SCHOLAR_API_KEY="your-key-here"
# Get free key: https://www.semanticscholar.org/product/api#api-key
```

**OpenAlex** (polite requests):
```bash
export OPENALEX_EMAIL="your-email@example.com"
```

### Direct Script Usage

All scripts support `--help`:

```bash
python skills/searching-ml-papers/tools/scripts/multi_search.py --help
python skills/analyzing-papers/tools/scripts/graph_algorithms.py --help
```

---

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/modaribrahim/A-Claude-Code-plugin-for-systematic-academic-paper-discovery-and-analysis.git
cd A-Claude-Code-plugin-for-systematic-academic-paper-discovery-and-analysis

# Install dependencies
cd skills/searching-ml-papers/tools && uv sync
cd ../analyzing-papers/tools && uv sync
```

### Install Pre-commit Hooks (Recommended)

```bash
pip install pre-commit
pre-commit install --install-hooks
```

**Pre-commit hooks include**:
- Ruff (Python linting/formatting)
- Markdownlint (doc quality)
- Gitleaks (secrets detection)

### Run Tests

```bash
python skills/searching-ml-papers/tools/test_multi_search.py
python skills/analyzing-papers/tools/test_build_network.py
```

**See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.**

---

## Documentation

- **[Architecture](docs/architecture.md)** - System design, data flow, components
- **[Contributing](CONTRIBUTING.md)** - Development setup, guidelines
- **[Changelog](CHANGELOG.md)** - Version history

---

## Troubleshooting

### "No sessions found"
→ Check `skills/searching-ml-papers/tools/artifacts/` directory

### "Import errors"
→ Run `uv sync` in skill's `tools/` directory

### "API rate limit"
→ Use optional API keys (see above)

### Need more help?
→ [Open an issue](https://github.com/modaribrahim/A-Claude-Code-plugin-for-systematic-academic-paper-discovery-and-analysis/issues)

---

## License

MIT License - see [LICENSE](LICENSE) file

---

## Acknowledgments

Built with:
- [Claude Code](https://docs.claude.com/claude-code)
- [uv](https://docs.astral.sh/uv/) - Fast package manager
- [Ruff](https://docs.astral.sh/ruff/) - Python linter

Data sources:
- [arXiv](https://arxiv.org/)
- [Semantic Scholar](https://www.semanticscholar.org/)
- [OpenAlex](https://openalex.org/)

---

**Made with ❤️ for researchers**
