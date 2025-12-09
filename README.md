# Demyst

> **de·mys·ti·fy** /dēˈmistəˌfī/ — make scientific code less obscure

[![PyPI version](https://badge.fury.io/py/demyst.svg)](https://badge.fury.io/py/demyst)
[![Tests](https://github.com/Hmbown/demyst/actions/workflows/ci.yml/badge.svg)](https://github.com/Hmbown/demyst/actions/workflows/ci.yml)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Demyst is a **static scientific linter**. Like `black` for formatting and `mypy` for types, it checks the logic of research code: leakage, statistical malpractice, mirages (information loss), unit/tensor mistakes, and gradient pathologies.

```bash
pip install demyst
demyst analyze ./src
```

## Status

| | |
|---|---|
| **Stability** | Alpha — actively developed, APIs may change |
| **Python** | 3.8–3.12 |
| **Ecosystems** | NumPy, pandas, SciPy, scikit-learn, PyTorch, JAX |
| **Philosophy** | Prefer early warnings over silence — suppress per line when intentional |

## What Demyst Catches

| Guard | Detects | Example |
|-------|---------|---------|
| `leakage` | Train/test contamination | `fit_transform()` before `train_test_split()` |
| `mirage` | Variance-/tail-destroying reductions | `np.mean()` hides outliers or fat tails |
| `hypothesis` | P-hacking, uncorrected multiplicity | 20 t-tests at α=0.05 without correction |
| `tensor` | Gradient death/normalization issues | Deep sigmoid chains; BatchNorm stats off |
| `units` | Dimensional mismatches | Adding meters to seconds |

## Why Teams Use It

- Catches silent scientific failures before peer review or production.
- Static: no data access, no runtime hooks; safe in CI.
- Actionable messages with suggested fixes.
- Configurable domain profiles (e.g., physics, clinical) and per-guard severities.

## Quick Start

```bash
git clone https://github.com/Hmbown/demyst.git
cd demyst
pip install -e .
demyst leakage examples/ml_data_leakage.py
```

## Sample Output

```text
──────────────────────────── Data Leakage Detected ─────────────────────────────
CRITICAL Line 47 in examples/ml_data_leakage.py
  fit_transform() called BEFORE train_test_split.
  Preprocessing learns from test data — your benchmark is invalid.

Fix: Split first, fit on train only, then transform test.
Summary: 1 critical issue
```

## Fast CLI Recipes

```bash
# Full project scan
demyst analyze path/to/code

# Focused checks
demyst mirage model.py
demyst leakage train.py
demyst hypothesis stats.py
demyst tensor network.py
demyst units physics.py

# Auto-fix mirages where safe
demyst mirage model.py --fix

# CI mode with nonzero exit on issues
demyst ci . --strict
```

## Domain Profiles and Config

Demyst ships domain profiles (biology, physics, economics, etc.) and accepts custom YAML.

`examples/configs/physics.yaml`:
```yaml
profile: physics
thresholds:
  significance: 5.0
unit_system: natural   # c = hbar = G = 1
tensor_conventions: true
allowed_mirages:
  - ensemble_average
required_statistics:
  - variance
  - background_rate
```

Project config `.demystrc.yaml`:
```yaml
profile: clinical
rules:
  mirage: {enabled: true, severity: critical}
  leakage: {enabled: true, severity: critical}
ignore_patterns:
  - "**/tests/**"
```

## Suppressing Warnings

```python
mean_value = np.mean(data)              # demyst: ignore
dashboard_avg = np.mean(daily_views)   # demyst: ignore-mirage
scaler.fit_transform(X)                # demyst: ignore-leakage
```

Available: `ignore`, `ignore-mirage`, `ignore-leakage`, `ignore-hypothesis`, `ignore-tensor`, `ignore-unit`, `ignore-all`.

## CI/CD Integration

**GitHub Actions**
```yaml
name: Demyst
on: [push, pull_request]
jobs:
  demyst:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install demyst
      - run: demyst ci . --strict
```

**Pre-commit**
```yaml
repos:
  - repo: https://github.com/Hmbown/demyst
    rev: v0.1.1a0
    hooks:
      - id: demyst
```

## Programmatic Use

```python
from demyst import LeakageHunter

source = open("model.py").read()
result = LeakageHunter().analyze(source)
if result["summary"]["critical_count"]:
    print("DATA LEAKAGE DETECTED")
```

## References and Further Reading

- Anscombe's Quartet — identical means, different shapes
- Simpson's Paradox — subgroup vs aggregate reversals
- Fat tails in finance — means hide crashes
- Retraction stats — computational errors are common

Resources: [Quick Start](docs/quickstart.md) · [Usage](docs/usage.md) · [Configs](examples/configs/) · [Notebook](notebooks/quickstart.ipynb)

## License

MIT — see [LICENSE](LICENSE)
