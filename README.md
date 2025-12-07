# Demyst

> **de·mys·ti·fy** /dēˈmistəˌfī/ — to make less obscure or confusing

A scientific linter for research code. Like `black` for formatting and `mypy` for types, `demyst` checks **scientific logic**.

```bash
pip install demyst
demyst analyze ./src
```

## What It Catches

| Check | What It Detects | Example |
|-------|-----------------|---------|
| `mirage` | Variance-destroying reductions | `np.mean()` hiding a rogue agent in a swarm |
| `leakage` | Train/test contamination | `fit_transform()` before `train_test_split()` |
| `hypothesis` | P-hacking, multiple comparisons | 20 t-tests without Bonferroni correction |
| `tensor` | Gradient death, normalization issues | Deep sigmoid chains, disabled BatchNorm stats |
| `units` | Dimensional mismatches | Adding meters to seconds |

## Quick Examples

**Mirage** — aggregations that hide critical variance:

```python
# DANGEROUS: 999 agents score 1.0, one scores 0.0
np.mean(agent_scores)  # Returns 0.999 — you deploy, rogue agent destroys system
```

**Leakage** — the #1 ML benchmarking error:

```python
# WRONG: Leaks test statistics into training
scaler.fit_transform(X)
X_train, X_test = train_test_split(X_scaled)

# CORRECT
X_train, X_test = train_test_split(X)
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)
```

**P-Hacking** — uncorrected multiple comparisons:

```python
# 20 tests at α=0.05 expects 1 false positive
for condition in conditions:
    if ttest(a[condition], b[condition]).pvalue < 0.05:
        print(f"{condition} significant!")  # No correction applied
```

## Usage

```bash
# Full analysis
demyst analyze your_code.py

# Individual guards
demyst mirage model.py
demyst leakage train.py
demyst hypothesis stats.py
demyst units physics.py
demyst tensor network.py

# Auto-fix mirages
demyst mirage model.py --fix

# CI mode
demyst ci . --strict
```

## Why Mirages Matter

These documented cases show how `np.mean()` hides critical information:

| Phenomenon | What Happened |
|------------|---------------|
| **Anscombe's Quartet** (1973) | Four datasets with identical mean (7.5) but completely different distributions |
| **Simpson's Paradox** (Berkeley 1973) | 44% male vs 35% female admission overall, but women admitted more in 4/6 departments |
| **Fat Tails in Finance** | Average daily return ~0.04% hides Black Monday's -22.6% single-day crash |
| **Outlier Masking** | Multiple outliers pull mean toward them, causing detection tests to fail |

Run `demyst mirage examples/real_world_mirages.py` to see detection in action.

## CI/CD

**GitHub Actions:**

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

**Pre-commit:**

```yaml
repos:
  - repo: https://github.com/demyst/demyst
    rev: v1.2.0
    hooks:
      - id: demyst
```

See [`examples/configs/`](examples/configs/) for more templates.

## Suppressing False Positives

Use inline comments to suppress specific warnings:

```python
# Suppress all demyst warnings on this line
mean_value = np.mean(data)  # demyst: ignore

# Suppress only mirage warnings
dashboard_avg = np.mean(daily_views)  # demyst: ignore-mirage

# Suppress only leakage warnings  
scaler.fit_transform(X)  # demyst: ignore-leakage
```

Available suppressions: `ignore`, `ignore-mirage`, `ignore-leakage`, `ignore-hypothesis`, `ignore-tensor`, `ignore-unit`, `ignore-all`

## Configuration

Create `.demystrc.yaml`:

```yaml
profile: default  # Or: biology, physics, chemistry, economics

rules:
  mirage:
    enabled: true
    severity: critical
  leakage:
    enabled: true
    severity: critical

ignore_patterns:
  - "**/tests/**"
```

## Programmatic API

```python
from demyst import TensorGuard, LeakageHunter, HypothesisGuard, UnitGuard

source = open('model.py').read()
result = LeakageHunter().analyze(source)

if result['summary']['critical_count'] > 0:
    print("DATA LEAKAGE DETECTED")
```

## References

| Phenomenon | Finding | Source |
|------------|---------|--------|
| Anscombe's Quartet | Identical means hide different distributions | [Anscombe (1973)](https://en.wikipedia.org/wiki/Anscombe%27s_quartet) |
| Simpson's Paradox | Trends reverse when aggregated | [UC Berkeley (1975)](https://discovery.cs.illinois.edu/dataset/berkeley/) |
| Fat Tails | Normal assumptions hide crashes | [Mandelbrot (1963)](https://en.wikipedia.org/wiki/Fat-tailed_distribution) |
| Retraction Stats | 18.9% from computational errors | [PMC5395722](https://pmc.ncbi.nlm.nih.gov/articles/PMC5395722/) |

## Resources

- [Quick Start Guide](docs/quickstart.md)
- [Interactive Notebook](notebooks/quickstart.ipynb)
- [Configuration Templates](examples/configs/)
- [Full Documentation](docs/usage.md)

## License

MIT — See [LICENSE](LICENSE)

---

*"The first principle is that you must not fool yourself—and you are the easiest person to fool."* — Richard Feynman
