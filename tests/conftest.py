"""
Configuration file for pytest.

This file sets up the Python path for tests to be able to import from the root directory.
"""
import os
import sys

# Add the root directory to sys.path for proper imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) 