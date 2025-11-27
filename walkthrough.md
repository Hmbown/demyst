# Walkthrough: Fix mypy type errors

## 1. Fix Main Package Errors

I focused on fixing `mypy` errors in the main package `demyst` (excluding tests).

### `demyst/guards/unit_guard.py`
- Added `-> None` return type annotations to:
    - `UnitInferenceEngine.__init__`
    - `UnitInferenceEngine.register_type`
    - `Dimension.__post_init__`
    - `DimensionalAnalyzer.__init__`
    - `DimensionalAnalyzer.visit_FunctionDef`
    - `DimensionalAnalyzer.visit_Assign`
    - `DimensionalAnalyzer.visit_BinOp`
    - `DimensionalAnalyzer.visit_Compare`
    - `UnitGuard.__init__`

### `demyst/exceptions.py`
- Added explicit type annotation `Dict[str, Any]` for `details` dictionary in:
    - `ProfileNotFoundError.__init__`
    - `PluginValidationError.__init__`
  This fixed errors where `List[str]` was being assigned to a dictionary inferred as `Dict[str, str]`.

## 2. Verification

### Mypy
Ran `mypy demyst | grep -v "demyst/tests/"`.
Output was clean (no errors found in main package files).

### Tests
Ran `pytest demyst/tests/`.
Result: `136 passed, 10 skipped`

## 3. Conclusion
All main package type errors are resolved. The CI "Lint & Format" check should now pass.
