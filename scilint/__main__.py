#!/usr/bin/env python3
"""
Scilint: The Scientific Integrity Platform

This module provides the entry point for running scilint as a module:
    python -m scilint

It delegates to the main CLI interface.
"""

import sys
from scilint.cli import main

if __name__ == '__main__':
    sys.exit(main())