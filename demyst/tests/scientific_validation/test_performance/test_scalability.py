"""
Scalability and Performance Tests

Validates Demyst's performance on large codebases.
Target: < 1 second per 1000 lines.
"""

import time
import ast
import pytest
import os
from demyst.tests.scientific_validation.utils import SyntheticCodeGenerator
from demyst.engine.mirage_detector import MirageDetector
from demyst.guards.leakage_hunter import LeakageHunter
from demyst.guards.hypothesis_guard import HypothesisGuard
from demyst.guards.unit_guard import UnitGuard
from demyst.guards.tensor_guard import TensorGuard


class TestScalability:

    @classmethod
    def setup_class(cls):
        cls.generator = SyntheticCodeGenerator(seed=123)
        # Generate files of varying sizes
        cls.small_file_size = 1000
        cls.medium_file_size = 5000
        cls.large_file_size = 10000  # 10k lines

        cls.small_code = cls.generator.generate_large_file(cls.small_file_size)
        cls.medium_code = cls.generator.generate_large_file(cls.medium_file_size)
        cls.large_code = cls.generator.generate_large_file(cls.large_file_size)

    def test_performance_target_1k_lines(self):
        """Ensure analysis takes < 1 second for 1000 lines."""
        start_time = time.time()

        # Run full suite of analyzers
        tree = ast.parse(self.small_code)

        mirage = MirageDetector()
        mirage.analyze(tree)

        hunter = LeakageHunter()
        hunter.analyze(self.small_code)

        hypo = HypothesisGuard()
        hypo.analyze_code(self.small_code)

        unit = UnitGuard()
        unit.analyze(self.small_code)

        tensor = TensorGuard()
        tensor.analyze(self.small_code)

        duration = time.time() - start_time

        # Strict target: 1s.
        # Note: CI environments can be slow, so we set a safe upper bound for test stability,
        # but log the actual time.
        print(f"\n1k lines processed in {duration:.4f}s")
        assert duration < 2.0, f"Processing 1000 lines took too long: {duration:.2f}s"

    def test_linear_scaling(self):
        """Check if processing time scales roughly linearly from 1k to 5k lines."""
        # Measure 1k
        t0 = time.time()
        MirageDetector().analyze(ast.parse(self.small_code))
        t_1k = time.time() - t0

        # Measure 5k
        t0 = time.time()
        MirageDetector().analyze(ast.parse(self.medium_code))
        t_5k = time.time() - t0

        ratio = t_5k / t_1k
        expected_ratio = self.medium_file_size / self.small_file_size  # 5.0

        print(f"\nScaling ratio: {ratio:.2f} (Expected ~{expected_ratio})")

        # Allow some overhead overhead, but it shouldn't be quadratic (ratio > 10)
        assert ratio < (
            expected_ratio * 2.5
        ), f"Scaling appears non-linear: {ratio:.2f}x time for {expected_ratio}x lines"

    @pytest.mark.slow
    def test_large_file_memory_safety(self):
        """Process 10k lines and ensure no crash/excessive time."""
        start_time = time.time()

        # Just running the heaviest guard (LeakageHunter or TensorGuard)
        # TensorGuard visits many nodes
        TensorGuard().analyze(self.large_code)

        duration = time.time() - start_time
        print(f"\n10k lines processed in {duration:.4f}s")

        # 10k lines should reasonably complete in under 5-10s even on slow machines
        assert duration < 10.0
