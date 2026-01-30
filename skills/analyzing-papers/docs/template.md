# Research Analysis Report Template

This document provides detailed templates for generating comprehensive research analysis reports with **full traceability** - every claim MUST be backed by specific paper references.

---

## Critical Requirements

### Traceability Rules

**EVERY claim must cite papers:**

✅ **Good:**
```markdown
- Transformer methods account for 45% of papers (N=75) [1-10]
- State Space Models emerged in 2025 (8 papers) [11-18]
- LEVIR-CD is the most popular dataset (used in 45 papers) [19-63]
```

❌ **Bad:**
```markdown
- Transformer methods are popular
- State Space Models are emerging
- LEVIR-CD is commonly used
```

### Citation Format

**In text:** Use numbered citations or inline references
```markdown
Method A shows 15% better accuracy [Paper 1, Paper 5, Paper 12].

According to Smith et al. [Paper 3], this approach...
```

**In tables:** Include paper references
```markdown
| Method | Papers | Key References |
|--------|--------|----------------|
| Transformer | 75 | [1,5,12,23,45,...] |
| CNN | 32 | [2,8,15,22,...] |
```

**Appendix:** Full paper list with IDs
```markdown
## Appendix A: References

[1] Paper Title A (Author et al., 2025) - https://arxiv.org/abs/xxxx
[2] Paper Title B (Author et al., 2025) - https://arxiv.org/abs/yyyy
...
```

---

## Template 1: Full Research Report

### Structure

```markdown
# [Research Topic]: Comprehensive Analysis Report

*Generated: [Date] | Papers Analyzed: [N] | Time Period: [Year Range]*

## Executive Summary

[Each bullet MUST cite papers]

- **[Finding 1]**: [Description] [Papers X,Y,Z]
- **[Finding 2]**: [Description] [Papers A,B,C]
- **[Finding 3]**: [Description] with [Metric] [Papers M,N,O]

**Key Insight**: [Most important finding] [Multiple papers]

## 1. Paper Collection Overview

### 1.1 Collection Statistics

| Metric | Value | Source |
|--------|-------|--------|
| Total Papers | [N] | [File: extracted_data.json] |
| Time Period | [Year] - [Year] | [File: temporal_data.json] |
| Sources | [arXiv: N, Semantic Scholar: N] | [File: extracted_data.json] |
| Avg Citations | [X] | [File: extracted_data.json] |
| Median Year | [Year] | [File: extracted_data.json] |

**Data File**: `./analyzing-papers/artifacts/extracted_data.json`

### 1.2 Data Quality

- Papers with abstracts: [N] ([X]%) [Source: extracted_data.json]
- Papers with citations: [N] ([X]%) [Source: extracted_data.json]
- Papers with full metadata: [N] ([X]%) [Source: extracted_data.json]

## 2. Research Landscape

### 2.1 Main Approaches/Methods Identified

[Discovered from reading papers - cite representative papers for each]

| Approach | Papers | Percentage | Representative Papers | Description |
|----------|--------|------------|----------------------|-------------|
| [Method A] | [count] | [X]% | [Papers 1,2,3] | [Your analysis based on those papers] |
| [Method B] | [count] | [X]% | [Papers 4,5,6] | [Your analysis based on those papers] |
| [Method C] | [count] | [X]% | [Papers 7,8,9] | [Your analysis based on those papers] |

**Analysis based on**: [N] papers from `extracted_data.json` [Lines X-Y]

### 2.2 Key Differences Between Approaches

[Cite papers that discuss differences]

- **[Approach A] vs [Approach B]**: [Difference] [Papers X,Y discuss this]
- **Strengths**: [Paper A says..., Paper B notes...]
- **Weaknesses**: [Paper C points out..., Paper D observes...]
- **Use Cases**: [Paper E recommends..., Paper F suggests...]

### 2.3 Datasets/Benchmarks

[If applicable]

| Dataset | Papers | Key Papers | Description | Availability |
|---------|--------|------------|-------------|--------------|
| [Dataset A] | [count] | [Papers 1,2,3] | [What papers say about it] | [Paper 1 mentions availability] |
| [Dataset B] | [count] | [Papers 4,5,6] | [What papers say about it] | [Paper 4 mentions availability] |

## 3. Citation Network Analysis

**Data Source**: `./analyzing-papers/artifacts/network_analysis.json`

### 3.1 Most Influential Papers

[Based on PageRank from graph_algorithms.py - cite algorithm output]

1. **[Paper Title]** ([Paper ID])
   - **PageRank Score**: [score] [Source: network_analysis.json]
   - **Citations**: [N] [Source: extracted_data.json]
   - **Year**: [Year]
   - **Why Influential**: [Your analysis of paper's contribution]
   - **Cited By**: [Papers that cite it, if available]
   - **Key Contribution**: [What the paper introduced] [Quote from abstract]

2. **[Paper Title]** ([Paper ID])
   - **PageRank Score**: [score]
   - **Citations**: [N]
   - **Year**: [Year]
   - **Why Influential**: [Your analysis]
   - **Key Contribution**: [What the paper introduced]

[Continue for top 5-10]

### 3.2 Research Communities

[Based on community detection from graph_algorithms.py]

Identified [N] research communities [Source: network_analysis.json]:

#### Community 1: [Community Name]

- **Papers**: [N] [Papers: list from network_analysis.json]
- **Percentage**: [X]% of total
- **Key Themes**: [Your analysis of common themes] [Based on reading papers]
- **Representative Papers**:
  - [Paper 1] - [Why representative]
  - [Paper 2] - [Why representative]
  - [Paper 3] - [Why representative]
- **Citation Patterns**: [How papers in this community cite each other]

#### Community 2: [Community Name]

- **Papers**: [N]
- **Percentage**: [X]%
- **Key Themes**: [Your analysis]
- **Representative Papers**: [Papers]
- **Citation Patterns**: [Analysis]

### 3.3 Bridge Papers

[Papers that connect communities - from betweenness analysis]

- **[Paper Title]** ([Paper ID])
  - **Betweenness Score**: [score] [Source: network_analysis.json]
  - **Bridges**: [Community A] and [Community B]
  - **How**: [Your analysis of why it bridges]
  - **References**: [Papers from both communities it connects]

## 4. Temporal Analysis

**Data Source**: `./analyzing-papers/artifacts/temporal_data.json`

### 4.1 Publication Volume

| Year | Papers | Growth | Cumulative | Source |
|------|--------|--------|------------|-------|
| [Year] | [count] | [X]% | [count] | temporal_data.json |
| [Year] | [count] | [X]% | [count] | temporal_data.json |

**Trend**: [Your interpretation] [Based on data in temporal_data.json]

### 4.2 Evolution of Approaches

[Track year by year - cite papers from each year]

#### [Year 1]

- **Total Papers**: [N] [Source: temporal_data.json]
- **Dominant Approaches**: [Most common methods] [Papers X,Y,Z]
- **Emerging Approaches**: [New methods first appearing] [Papers A,B,C]
- **Declining Approaches**: [Methods fading] [Fewer papers than previous year]
- **Key Papers**:
  - [Paper 1] - [Why important]
  - [Paper 2] - [Why important]
  - [Paper 3] - [Why important]

#### [Year 2]

- **Total Papers**: [N]
- **Dominant Approaches**: [Papers X,Y,Z]
- **Emerging Approaches**: [Papers A,B,C]
- **Declining Approaches**: [Analysis]
- **Key Papers**: [Papers]

### 4.3 Trend Analysis

**Data Sources**: temporal_data.json + extracted_data.json

**📈 Growing Trends**:
- **[Trend 1]**: [X]% → [Y]% ([Year] → [Year]) [Papers showing this: 1,2,3,...]
- **[Trend 2]**: [X]% → [Y]% [Papers: 4,5,6,...]

**🔻 Declining Trends**:
- **[Trend 1]**: [X]% → [Y]% [Fewer papers: 7,8,...]
- **[Trend 2]**: [X]% → [Y]% [Fewer papers: 9,10,...]

**🔺 Emerging in [Year]**:
- **[Trend 1]**: [First appeared in Paper X], now [N] papers [Papers X,Y,Z,...]
- **[Trend 2]**: [First appeared in Paper A], now [N] papers [Papers A,B,C,...]

**Interpretation**: [Your analysis of what these trends mean] [Supported by papers X,Y,Z]

## 5. Statistical Insights

**Data Sources**:
- `./analyzing-papers/artifacts/citation_distribution.json`
- `./analyzing-papers/artifacts/venue_analysis.json`
- `./analyzing-papers/artifacts/correlations.json`

### 5.1 Citation Distribution

| Metric | Value | Source |
|--------|-------|--------|
| Mean | [X] | citation_distribution.json |
| Median | [X] | citation_distribution.json |
| Std Dev | [X] | citation_distribution.json |
| Min | [X] | citation_distribution.json |
| Max | [X] | citation_distribution.json |
| Q1 | [X] | citation_distribution.json |
| Q3 | [X] | citation_distribution.json |

**Outliers**: [N] papers with unusually high/low citations [Source: citation_distribution.json]

**Top Cited Papers**:
1. [Paper] - [N] citations
2. [Paper] - [N] citations
3. [Paper] - [N] citations

### 5.2 Venue Analysis

| Venue | Papers | Avg Citations | Quality | Source |
|-------|--------|---------------|---------|--------|
| [Venue A] | [N] | [X] | [Your assessment] | venue_analysis.json |
| [Venue B] | [N] | [X] | [Your assessment] | venue_analysis.json |
| [Venue C] | [N] | [X] | [Your assessment] | venue_analysis.json |

**Analysis**: [Your interpretation of venue quality] [Based on papers from each venue]

### 5.3 Author Productivity

| Author | Papers | Total Citations | Avg Citations | Key Papers | Source |
|--------|--------|-----------------|---------------|-------------|--------|
| [Author A] | [N] | [X] | [Y] | [Papers] | extracted_data.json |
| [Author B] | [N] | [X] | [Y] | [Papers] | extracted_data.json |

## 6. Research Gaps and Opportunities

**Based on analysis of all papers - cite what IS NOT there**

### 6.1 Underexplored Areas

[Identify by searching for what's NOT discussed]

1. **[Gap 1]**: [Description] - [Why important]
   - **Current State**: [What exists] [Papers A,B]
   - **What's Missing**: [What no paper addresses]
   - **Opportunity**: [Why this is a research gap] [0 papers found on this]

2. **[Gap 2]**: [Description] - [Why important]
   - **Current State**: [What exists] [Papers C,D]
   - **What's Missing**: [What no paper addresses]
   - **Opportunity**: [Research opportunity]

### 6.2 Method-Dataset Combinations Not Explored

| Method | Dataset | Papers Found | Opportunity |
|--------|---------|--------------|-------------|
| [Method A] | [Dataset X] | 0 | [Why interesting] |
| [Method B] | [Dataset Y] | 0 | [Why interesting] |

**Evidence**: [Searched through [N] papers, none mention this combination] [Source: extracted_data.json]

### 6.3 Contradictory Findings

[Areas where papers disagree - cite both sides]

- **[Topic]**:
  - **Claim A**: [Paper X says Y] [Paper X, abstract]
  - **Claim B**: [Paper Z says W] [Paper Z, abstract]
  - **Possible Resolution**: [Your analysis]
  - **Need**: [Future research to resolve]

### 6.4 Suggested Research Directions

[Based on gaps and trends - cite papers that motivate these]

1. **[Direction 1]**: [Description]
   - **Motivation**: [Papers X,Y,Z demonstrate need]
   - **Expected Impact**: [What it would enable]
   - **Feasibility**: [Why doable]
   - **Starting Point**: [Build on papers A,B]

2. **[Direction 2]**: [Description]
   - **Motivation**: [Papers]
   - **Expected Impact**: [What it would enable]
   - **Feasibility**: [Why doable]
   - **Starting Point**: [Build on papers]

## 7. Recommendations

### 7.1 For Researchers Starting in This Area

**Papers to Read First** [Cite with reasons]:
1. **[Paper 1]** - [Why most important] [Highest PageRank]
2. **[Paper 2]** - [Why important] [Survey paper]
3. **[Paper 3]** - [Why important] [Highly cited]

**Methods to Learn** [Cite papers]:
- **[Method A]** - [Why important] - [Key papers: X,Y,Z]
- **[Method B]** - [Why important] - [Key papers: A,B,C]

**Datasets to Use** [Cite papers]:
- **[Dataset A]** - [Why] - [Availability] - [Used in papers: X,Y,Z]
- **[Dataset B]** - [Why] - [Availability] - [Used in papers: A,B,C]

### 7.2 For Practitioners

**Recommended Approaches** [Cite evidence]:
- **Use [Method A] when**: [Use case] [Papers X,Y show this works best]
- **Use [Method B] when**: [Use case] [Papers A,B recommend this]
- **Avoid [Method C] when**: [Use case] [Papers C,D warn against this]

**Performance Expectations** [Cite specific results]:
- **State-of-the-art**: [Method] achieves [metric] [Paper X reports Y%]
- **Efficient option**: [Method] achieves [metric] with [X] less compute [Paper Y]
- **Robust option**: [Method] performs well across [conditions] [Paper Z]

### 7.3 For Future Research

**High-Potential Directions** [Cite motivating papers]:
1. **[Direction 1]**:
   - **Why Promising**: [Papers X,Y,Z demonstrate potential]
   - **Key Challenges**: [Paper A identifies challenge B]
   - **Expected Timeline**: [Your estimate]
   - **Building On**: [Papers that laid groundwork]

2. **[Direction 2]**:
   - **Why Promising**: [Papers]
   - **Key Challenges**: [Papers]
   - **Expected Timeline**: [Estimate]
   - **Building On**: [Papers]

**Avoid** [Cite evidence]:
- **[Saturated area]**: [Too many papers, high competition] [N papers in 2025]
- **[Dead end]**: [Why not promising] [Papers X,Y show limitations]

## 8. Appendices

### Appendix A: All Papers Analyzed

**Data Source**: `./analyzing-papers/artifacts/extracted_data.json`

| ID | Title | Authors | Year | Citations | URL |
|----|-------|---------|------|----------|-----|
| [1] | [Title] | [First author] | [Year] | [N] | [URL] |
| [2] | [Title] | [First author] | [Year] | [N] | [URL] |
| [3] | [Title] | [First author] | [Year] | [N] | [URL] |

**Total**: [N] papers

### Appendix B: Methodology

**Data Collection**:
- **Sources**: [Where papers came from]
- **Search Query**: [What query was used]
- **Time Period**: [Years covered]
- **Inclusion Criteria**: [How papers were selected]

**Analysis Methods**:
- **Scripts Used**: [Which scripts and versions]
- **Data Files**: [List all generated files]
  - `extracted_data.json` - [What it contains]
  - `temporal_data.json` - [What it contains]
  - `network_analysis.json` - [What it contains]
  - `citation_distribution.json` - [What it contains]

**Analysis Steps**:
1. Extract data using `extract_data.py`
2. Build temporal organization using `extract_temporal.py`
3. Run graph algorithms using `graph_algorithms.py`
4. Run statistical analysis using `statistical_tools.py`
5. Read sample papers to understand domain
6. Identify patterns and trends
7. Generate this report

**Reproducibility**:
All data files saved in `./analyzing-papers/artifacts/`

### Appendix C: Statistical Details

**Citation Distribution** [Source: citation_distribution.json]:
- [Full statistics]
- [Histogram data]
- [Outlier analysis]

**Venue Analysis** [Source: venue_analysis.json]:
- [Full frequency table]
- [All venues and counts]

**Correlations** [Source: correlations.json]:
- [Full correlation matrix]
- [All pairwise correlations]

---

## Notes for Agent

### When Using This Template:

1. **EVERY claim must cite papers**
   - Use numbered citations: [1], [2], [3]
   - Or inline: [Paper 1], [Paper 2]
   - Or in tables: Include "Key Papers" column

2. **Always reference data sources**
   - Mention which file contains the data
   - Example: [Source: extracted_data.json]
   - Example: [Source: network_analysis.json]

3. **Be specific about evidence**
   - "According to Paper X, ..." not "Some papers suggest..."
   - "Papers 1, 2, 3 demonstrate..." not "Several papers show..."

4. **Enable verification**
   - Include paper IDs
   - Include URLs
   - Include citation counts
   - Include years

5. **Appendix A is CRITICAL**
   - Must include ALL papers
   - Number them for easy referencing
   - Include all metadata

### Note
All templates should begin with this:
**Disclaimer**: All results produced here are based on papers' abstracts and titles only !
### What Makes Good Traceability:

✅ **Good**:
- "Transformer methods account for 45% of papers (N=75) [Papers 1-10, 15-20, ...]"
- "According to Smith et al. [Paper 5], accuracy improved by 15%"
- Table includes "Key Papers" column with references

❌ **Bad**:
- "Transformer methods are popular" (Which papers? How many?)
- "Accuracy improved significantly" (What paper? How much?)
- "Most papers use LEVIR-CD" (Most? How many? Which ones?)

### Verification Checklist:

- [ ] Every claim has paper citation
- [ ] Tables reference specific papers
- [ ] Appendix A lists ALL papers
- [ ] Data sources are referenced
- [ ] Reader can verify every claim
- [ ] Results are reproducible from data files
