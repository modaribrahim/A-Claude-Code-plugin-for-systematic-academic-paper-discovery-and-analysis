#!/usr/bin/env python3
"""
Basic tests for multi_search.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test that all required modules can be imported"""
    try:
        import requests
        import arxiv
        import click
        import numpy
        print("✓ All required modules imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

def test_script_exists():
    """Test that multi_search.py exists and is executable"""
    script_path = os.path.join(os.path.dirname(__file__), "scripts", "multi_search.py")
    if os.path.exists(script_path):
        print(f"✓ multi_search.py found at: {script_path}")
        return True
    else:
        print(f"✗ multi_search.py not found at: {script_path}")
        return False

def test_arxiv_client_exists():
    """Test that arxiv_client.py exists"""
    client_path = os.path.join(os.path.dirname(__file__), "arxiv_client.py")
    if os.path.exists(client_path):
        print(f"✓ arxiv_client.py found")
        return True
    else:
        print(f"✗ arxiv_client.py not found")
        return False

def test_utils_directory_exists():
    """Test that utils directory exists"""
    utils_path = os.path.join(os.path.dirname(__file__), "utils")
    if os.path.exists(utils_path):
        print(f"✓ utils directory found")
        return True
    else:
        print(f"✗ utils directory not found")
        return False

if __name__ == "__main__":
    print("Running basic tests for searching-ml-papers...")
    print()

    tests = [
        test_imports,
        test_script_exists,
        test_arxiv_client_exists,
        test_utils_directory_exists,
    ]

    results = [test() for test in tests]

    print()
    if all(results):
        print("✓ All tests passed!")
        sys.exit(0)
    else:
        print("✗ Some tests failed")
        sys.exit(1)
