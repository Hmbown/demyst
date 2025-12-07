"""
Performance smoke tests for Demyst analysis.

Goal: Ensure core guards handle moderately large code in reasonable time.
This is intentionally loose to avoid flakiness; it guards against regressions.
"""

import time

import pytest

from demyst.engine.mirage_detector import MirageDetector
from demyst.guards.leakage_hunter import LeakageHunter
from demyst.tests.scientific_validation.utils import SyntheticCodeGenerator


class TestPerformanceSmoke:
    @pytest.mark.slow
    def test_mirage_detector_throughput(self):
        """MirageDetector should analyze ~2000 lines within a loose threshold."""
        generator = SyntheticCodeGenerator(seed=123)
        code = generator.generate_large_file(num_lines=2000)

        detector = MirageDetector()
        start = time.perf_counter()
        detector.analyze(__import__("ast").parse(code))
        duration = time.perf_counter() - start

        # Allow generous threshold to avoid flakiness; regression guard only
        assert duration < 5.0, f"MirageDetector too slow: {duration:.2f}s"

    @pytest.mark.slow
    def test_leakage_hunter_throughput(self):
        """LeakageHunter should analyze ~1000 lines within a loose threshold."""
        generator = SyntheticCodeGenerator(seed=321)
        code = generator.generate_large_file(num_lines=1000)

        hunter = LeakageHunter()
        start = time.perf_counter()
        hunter.analyze(code)
        duration = time.perf_counter() - start

        assert duration < 5.0, f"LeakageHunter too slow: {duration:.2f}s"
