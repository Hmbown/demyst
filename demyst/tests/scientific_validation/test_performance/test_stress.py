"""
Edge Case Stress Testing

Robustness under extreme conditions: nested calls, long lines, complexity.
"""

import ast
import textwrap
import pytest
from demyst.guards.unit_guard import UnitGuard
from demyst.guards.tensor_guard import TensorGuard


class TestCodeComplexity:

    def test_deeply_nested_calls(self):
        """Test parsing and analysis of deeply nested function calls."""
        # f(f(f(...)))
        depth = 200
        nested_call = "x"
        for _ in range(depth):
            nested_call = f"f({nested_call})"

        code = f"result = {nested_call}"

        # UnitGuard tracks calls
        guard = UnitGuard()
        result = guard.analyze(code)

        # Should not crash
        verdict = result["summary"]["verdict"]
        assert any(status in verdict for status in ["PASS", "WARNING", "FAIL"])

    def test_extremely_long_lines(self):
        """Test extremely long lines (e.g. hardcoded data)."""
        # Generate a 100k char line
        long_list = ",".join([str(i) for i in range(10000)])
        code = f"data = [{long_list}]"

        guard = TensorGuard()
        result = guard.analyze(code)
        assert result["summary"] is not None


class TestContentEdgeCases:

    def test_unicode_identifiers(self):
        """Test unicode math symbols in variable names."""
        code = textwrap.dedent(
            """
            def physics_calc(α, β, Δt):
                # Unicode variables
                ω = α * β
                θ = ω * Δt
                return θ
        """
        )

        guard = UnitGuard()
        result = guard.analyze(code)
        # Should handle unicode without error
        assert len(result["violations"]) == 0

    def test_complex_lambda_expressions(self):
        """Test lambda functions with complex logic."""
        code = textwrap.dedent(
            """
            f = lambda x, y: (x**2 + y**2)**0.5 if x > 0 else 0
            
            # Nested lambdas
            g = lambda a: (lambda b: a + b)(10)
        """
        )

        guard = UnitGuard()
        result = guard.analyze(code)
        assert result["summary"] is not None
