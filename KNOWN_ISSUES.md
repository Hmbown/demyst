# Scilint v1.1 - Known Issues & Quick Fixes

## Minor Issues to Address

### 1. Missing `__init__.py` in tests directory
```bash
touch scilint/tests/__init__.py
```

### 2. CLI mirage command uses old transpiler import
The `mirage_command` should integrate with the original transpiler for transformation capability.

### 3. Taint Analysis Needs Parent Node Assignment
In `leakage_hunter.py`, the `_add_parent_refs` method should be called before visiting.

### 4. Domain-Specific Rule Sets Missing
Scientists in different fields need customizable rule sets (physics, biology, economics).

## Recommended Additions for Launch

1. **Config file support** (`.scilintrc.yaml`)
2. **Pre-commit hook configuration**
3. **VS Code extension** (LSP integration)
4. **Domain-specific profiles** (physics, biology, finance)
5. **Interactive fix suggestions** (auto-fix mode)
