"""
Test package initialization.

This file adds the project root to the Python path for imports.
"""
import os
import sys

# Add the root directory to sys.path for proper imports
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
