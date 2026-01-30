#!/usr/bin/env python3
"""
Basic tests for build_network.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test that all required modules can be imported"""
    try:
        import requests
        import numpy
        print("✓ All required modules imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

def test_script_exists():
    """Test that build_network.py exists"""
    script_path = os.path.join(os.path.dirname(__file__), "scripts", "build_network.py")
    if os.path.exists(script_path):
        print(f"✓ build_network.py found at: {script_path}")
        return True
    else:
        print(f"✗ build_network.py not found at: {script_path}")
        return False

def test_graph_algorithms_exists():
    """Test that graph_algorithms.py exists"""
    script_path = os.path.join(os.path.dirname(__file__), "scripts", "graph_algorithms.py")
    if os.path.exists(script_path):
        print(f"✓ graph_algorithms.py found")
        return True
    else:
        print(f"✗ graph_algorithms.py not found")
        return False

def test_select_input_exists():
    """Test that select_input.py exists"""
    script_path = os.path.join(os.path.dirname(__file__), "scripts", "select_input.py")
    if os.path.exists(script_path):
        print(f"✓ select_input.py found")
        return True
    else:
        print(f"✗ select_input.py not found")
        return False

if __name__ == "__main__":
    print("Running basic tests for analyzing-papers...")
    print()

    tests = [
        test_imports,
        test_script_exists,
        test_graph_algorithms_exists,
        test_select_input_exists,
    ]

    results = [test() for test in tests]

    print()
    if all(results):
        print("✓ All tests passed!")
        sys.exit(0)
    else:
        print("✗ Some tests failed")
        sys.exit(1)
