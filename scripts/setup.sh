#!/bin/bash
set -e

# Research Companion - Manual Setup Script
# This is a fallback script. Normal installation uses the post-install hook.

echo "======================================"
echo "Research Companion - Manual Setup"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_DIR="$(dirname "$SCRIPT_DIR")"

echo "Plugin directory: $PLUGIN_DIR"
echo ""

# 1. Check Python installation
echo "Step 1: Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed!"
    echo "Please install Python 3.9 or higher from https://www.python.org/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
print_success "Python found: $PYTHON_VERSION"

# Check Python version >= 3.9
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 9 ]); then
    print_error "Python 3.9 or higher is required (found $PYTHON_VERSION)"
    exit 1
fi

echo ""

# 2. Check uv installation (REQUIRED)
echo "Step 2: Checking uv installation..."
if ! command -v uv &> /dev/null; then
    print_error "uv is not installed!"
    echo ""
    echo "uv is required for dependency management."
    echo ""
    echo "Install uv using one of these methods:"
    echo "  1. Standalone installer (recommended):"
    echo "     curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo ""
    echo "  2. Using pip:"
    echo "     pip install uv"
    echo ""
    echo "  3. Using homebrew (macOS):"
    echo "     brew install uv"
    echo ""
    echo "For more options, see: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
fi

UV_VERSION=$(uv --version | cut -d' ' -f2)
print_success "uv found: $UV_VERSION"
echo ""

# 3. Install dependencies for searching-ml-papers skill
echo "Step 3: Installing dependencies for searching-ml-papers skill..."
SEARCHING_TOOLS="$PLUGIN_DIR/skills/searching-ml-papers/tools"

if [ ! -d "$SEARCHING_TOOLS" ]; then
    print_error "Tools directory not found: $SEARCHING_TOOLS"
    exit 1
fi

cd "$SEARCHING_TOOLS"

if [ -f "pyproject.toml" ]; then
    print_info "Found pyproject.toml"
    if uv sync; then
        print_success "Dependencies installed for searching-ml-papers"
    else
        print_error "Failed to install dependencies"
        exit 1
    fi
else
    print_error "pyproject.toml not found in $SEARCHING_TOOLS"
    exit 1
fi

echo ""

# 4. Install dependencies for analyzing-papers skill
echo "Step 4: Installing dependencies for analyzing-papers skill..."
ANALYZING_TOOLS="$PLUGIN_DIR/skills/analyzing-papers/tools"

cd "$ANALYZING_TOOLS"

if [ -f "pyproject.toml" ]; then
    print_info "Found pyproject.toml"
    if uv sync; then
        print_success "Dependencies installed for analyzing-papers"
    else
        print_error "Failed to install dependencies"
        exit 1
    fi
else
    print_error "pyproject.toml not found in $ANALYZING_TOOLS"
    exit 1
fi

echo ""

# 5. Verify critical imports
echo "Step 5: Verifying installation..."

# Check imports using the searching skill's virtual environment
if [ -f "$SEARCHING_TOOLS/.venv/bin/python3" ]; then
    PYTHON_BIN="$SEARCHING_TOOLS/.venv/bin/python3"
elif [ -f "$SEARCHING_TOOLS/.venv/bin/python" ]; then
    PYTHON_BIN="$SEARCHING_TOOLS/.venv/bin/python"
else
    PYTHON_BIN="python3"
fi

$PYTHON_BIN -c "
import sys
try:
    import requests
    import arxiv
    import click
    import numpy
    import sentence_transformers
    print('All core dependencies imported successfully')
except ImportError as e:
    print(f'Import error: {e}')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    print_success "All core dependencies verified"
else
    print_error "Dependency verification failed"
    exit 1
fi

echo ""

# 6. Test script accessibility
echo "Step 6: Verifying script paths..."

SEARCHING_SCRIPTS=(
    "$SEARCHING_TOOLS/scripts/multi_search.py"
    "$SEARCHING_TOOLS/scripts/citation_expand.py"
)

for script in "${SEARCHING_SCRIPTS[@]}"; do
    if [ -f "$script" ]; then
        print_success "Found: $(basename $script)"
    else
        print_error "Missing: $script"
    fi
done

ANALYZING_SCRIPTS=(
    "$ANALYZING_TOOLS/scripts/select_input.py"
    "$ANALYZING_TOOLS/scripts/build_network.py"
)

for script in "${ANALYZING_SCRIPTS[@]}"; do
    if [ -f "$script" ]; then
        print_success "Found: $(basename $script)"
    else
        print_error "Missing: $script"
    fi
done

echo ""

# 7. Create artifacts directories
echo "Step 7: Setting up artifacts directories..."

mkdir -p "$SEARCHING_TOOLS/artifacts"
mkdir -p "$ANALYZING_TOOLS/artifacts"

print_success "Artifacts directories ready"
echo ""

# 8. Optional API keys check
echo "Step 8: Checking for API keys (optional)..."
echo ""
echo "The following API keys are optional but recommended for better results:"
echo ""
echo "  • Semantic Scholar API: https://www.semanticscholar.org/product/api#api-key"
echo "    Set as: SEMANTIC_SCHOLAR_API_KEY"
echo ""
echo "  • OpenAlex (no key required, but email recommended):"
echo "    Set as: OPENALEX_EMAIL"
echo ""

if [ -n "$SEMANTIC_SCHOLAR_API_KEY" ]; then
    print_success "Semantic Scholar API key found"
else
    print_warning "Semantic Scholar API key not set (optional)"
fi

if [ -n "$OPENALEX_EMAIL" ]; then
    print_success "OpenAlex email found"
else
    print_warning "OpenAlex email not set (optional)"
fi

echo ""

# 9. Summary
echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo ""
print_success "Research Companion is ready to use"
echo ""
echo "📦 Modern Python packaging with uv:"
echo "  • Dependencies managed per-skill via pyproject.toml"
echo "  • Each skill has its own virtual environment"
echo "  • Virtual environments: skills/*/tools/.venv/"
echo ""
echo "Next steps:"
echo "  1. Set optional API keys as environment variables"
echo "  2. Restart Claude Code to activate the plugin"
echo "  3. Use the skills:"
echo "     - searching-ml-papers: Find academic papers"
echo "     - analyzing-papers: Analyze citation networks"
echo ""
echo "For more information, see: $PLUGIN_DIR/README.md"
echo ""
