# Contributing to Research Companion

Thank you for your interest in contributing! This guide will help you get started.

## Quick Links

- [Report a bug](https://github.com/modaribrahim/A-Claude-Code-plugin-for-systematic-academic-paper-discovery-and-analysis/issues)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Claude Code Documentation](https://docs.claude.com/claude-code)
- [Semantic Versioning](https://semver.org/)

## Overview

Research Companion is a Claude Code plugin for systematic academic paper discovery and analysis. It combines multi-source search (arXiv, Semantic Scholar, OpenAlex) with citation network analysis and statistical tools.

## Local Development Setup

### 1. Fork and Clone

```bash
git clone https://github.com/YOUR_USERNAME/A-Claude-Code-plugin-for-systematic-academic-paper-discovery-and-analysis.git
cd A-Claude-Code-plugin-for-systematic-academic-paper-discovery-and-analysis
```

### 2. Navigate to Plugin Directory

```bash
cd research-companion
```

### 3. Install uv (if not already installed)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# or: pip install uv
```

### 4. Install Dependencies

```bash
# Install all dependencies
uv sync

# Or run the setup script
bash scripts/setup.sh
```

### 5. Set Up Pre-commit Hooks (Recommended)

Pre-commit hooks automatically check and fix code quality issues before you commit.

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install --install-hooks

# Optional: Install pre-push hook to run tests
pre-commit install --hook-type pre-push
```

**Pre-commit hooks include:**
- Python formatting and linting (ruff)
- Trailing whitespace and EOF fixes
- YAML/JSON validation
- Markdown linting
- Large file prevention
- Secrets detection (gitleaks)

Run on all files: `pre-commit run --all-files`

### 6. Configure Commit Template (Optional)

```bash
git config commit.template .gitmessage
```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b your-feature-name
```

### 2. Understand the Structure

```
research-companion/
├── skills/                    # Claude Code skills
│   ├── searching-ml-papers/   # Paper discovery skill
│   │   └── SKILL.md
│   └── analyzing-papers/      # Analysis skill
│       └── SKILL.md
├── searching-papers-v2/       # Search system
│   ├── scripts/               # Python scripts
│   ├── clients/               # API clients
│   └── utils/                 # Utilities
├── analyzing-papers/          # Analysis system
│   └── scripts/               # Python scripts
├── hooks/                     # Plugin hooks
├── pyproject.toml             # Dependencies
└── uv.lock                    # Locked versions
```

### 3. Make Changes

- Follow existing code style
- Use descriptive variable names
- Add comments for complex logic
- Update documentation as needed

### 4. Test Your Changes

```bash
# Test paper search
python searching-papers-v2/scripts/multi_search.py --query "test query" --max-results 10

# Test analysis scripts
python analyzing-papers/scripts/build_network.py --help
```

### 5. Commit Using Conventional Commits

We use [Conventional Commits](https://www.conventionalcommits.org/) for structured commit messages:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```bash
git commit -m "feat(searching): add OpenAlex API integration"
git commit -m "fix(analyzing): resolve PageRank calculation error"
git commit -m "docs: update installation instructions"
```

### 6. Push and Create Pull Request

```bash
git push origin your-feature-name
```

Then create a pull request on GitHub with:
- Clear description of changes
- References to related issues
- Screenshots if applicable

## Code Quality Standards

### Python Style

We use **Ruff** for fast Python linting and formatting (replaces black, isort, flake8).

**Configuration:** See `ruff.toml`

**Manual checks:**
```bash
# Check issues
ruff check .

# Fix issues automatically
ruff check --fix .

# Format code
ruff format .
```

### Documentation Style

- Use clear, concise language
- Provide examples for complex features
- Update README.md for user-facing changes
- Update CHANGELOG.md for significant changes

### Testing

While we don't have automated tests yet, please:
- Manually test your changes
- Test edge cases (empty results, API failures, etc.)
- Verify with multiple paper sources

## Adding New Features

### Adding a New Data Source

1. Create client in `searching-papers-v2/`
2. Update `multi_search.py` to integrate
3. Update SKILL.md documentation
4. Add example usage

### Adding Analysis Methods

1. Add script to `analyzing-papers/scripts/`
2. Update `analyzing-papers/SKILL.md`
3. Test with real data
4. Document algorithm

## Reporting Issues

When reporting bugs, please include:

- **Clear description** of the problem
- **Steps to reproduce** the issue
- **Expected behavior** vs actual behavior
- **Environment details** (OS, Python version, Claude Code version)
- **Error messages** or logs
- **Minimal example** if applicable

## Suggesting Features

We welcome feature suggestions! Please:

- Check existing issues first
- Describe the use case clearly
- Explain why it would be useful
- Consider if it fits the project scope

## Project Philosophy

Research Companion aims to be:

- **Generic**: No hardcoded domains, works across fields
- **Traceable**: Every claim cites specific papers
- **Extensible**: Easy to add new sources and analysis methods
- **Professional**: Modern packaging, automated quality checks

When contributing, keep these principles in mind.

## Getting Help

- **Documentation**: See README.md and SKILL.md files
- **Issues**: Check existing GitHub issues
- **Discussions**: Use GitHub Discussions for questions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Research Companion! 🎓📚
