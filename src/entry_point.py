#!/usr/bin/env python3
"""
Entry point wrapper for epub-to-pdf command
"""

import sys
import os

# Add the root directory to Python path so we can import main
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)

from main import main

if __name__ == "__main__":
    main()