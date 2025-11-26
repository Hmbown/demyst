#!/usr/bin/env python3
"""
Scilint Main Entry Point
"""

import sys
import os

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scilint.__main__ import main

if __name__ == '__main__':
    main()