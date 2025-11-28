"""
Demyst Test Configuration and Fixtures

Provides shared fixtures for all test modules:
- Path fixtures for project root and examples directory
- Source code fixtures for each example file
- Guard instance fixtures (mirage_detector, hypothesis_guard, unit_guard)
"""

from pathlib import Path

import pytest


# Project root detection
@pytest.fixture(scope="session")
def project_root() -> Path:
    """Return the project root directory."""
    return Path(__file__).parent.parent.parent

