# Demyst

> **de·mys·ti·fy** /dēˈmistəˌfī/ *transitive verb*
> 1. To eliminate the mystifying features of.
> 2. To make less obscure, unclear, or confusing.

**Demyst** is a scientific linter that ensures your code means what you think it means. Just as `black` formats your code and `mypy` checks your types, `demyst` checks your **scientific logic**.

> "Science is the belief in the ignorance of experts." - Richard Feynman

![Demyst Demo](demo.gif)

## Why Demyst?

In the age of AI and rapid prototyping, we face a fundamental challenge:

**How do we know our computation is trustworthy, not just its output?**

Standard linters catch syntax errors. Demyst catches **scientific logic errors**:
- Using `mean()` on heavy-tailed distributions (hiding outliers).
- Leaking test data into training sets.
- P-hacking by running multiple tests without correction.
- Adding meters to seconds.

Demyst is designed to be a ubiquitous part of your research workflow. Run a **Demyst Check** before you commit, before you publish, and before you trust the result.


## What Demyst Detects

### 1. Computational Mirages
Operations that destroy variance/distribution information:

```python
# DANGEROUS: Hides the rogue agent in a swarm of 1000
mean_score = np.mean(agent_scores)  # Returns 0.999, but one agent is 0.0!

# SAFE: Preserves distribution for inspection
scores = VariationTensor(agent_scores).collapse('mean')  # Keeps variance metadata
```

### 2. Data Leakage
The #1 error in machine learning that invalidates benchmarks:

```python
# WRONG: Fits scaler on ALL data before split
scaler.fit_transform(X)  # Leaks test statistics into training!
X_train, X_test = train_test_split(X_scaled)

# CORRECT: Fit only on training data
X_train, X_test = train_test_split(X)
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)
```

### 3. P-Hacking & Statistical Validity
Uncorrected multiple comparisons that inflate false positives:

```python
# PROBLEMATIC: 20 tests at alpha=0.05 expects 1 false positive!
for condition in conditions:
    p = ttest(group_a[condition], group_b[condition])
    if p < 0.05:  # No correction applied
        print(f"{condition} is significant!")

# Demyst recommends: Bonferroni, Holm-Bonferroni, or Benjamini-Hochberg correction
```

### 4. Deep Learning Integrity
Gradient death, normalization blindness, and reward hacking:

```python
# PROBLEMATIC: Deep sigmoid chains cause vanishing gradients
x = torch.sigmoid(fc1(x))
x = torch.sigmoid(fc2(x))
x = torch.sigmoid(fc3(x))  # Gradients approaching 0

# PROBLEMATIC: BatchNorm hides distribution shift
self.bn = nn.BatchNorm2d(64, track_running_stats=False)  # Masks drift!
```

### 5. Dimensional Analysis
Unit mismatches that violate physical laws:

```python
# WRONG: Adding meters to seconds is physically meaningless
result = distance_meters + time_seconds

# Demyst detects: "Cannot add quantities with dimensions [L] and [T]"
```

## What Demyst Catches

Demyst is designed to catch **scientific logic errors** that standard linters miss.

| Domain | Error Type | Example |
|--------|------------|---------|
| **General Science** | **Computational Mirages** | Calculating `mean()` on a swarm where variance is critical (e.g., 1 rogue agent). |
| **Physics** | **Dimensional Analysis** | Adding `time` to `distance` or assigning `energy` to `force`. |
| **Biology** | **P-Hacking** | Running 1,000 t-tests in a loop without Bonferroni correction. |
| **Chemistry** | **Stoichiometry** | Adding `mass` (grams) to `moles` directly. |
| **Machine Learning** | **Data Leakage** | Scaling data before splitting into train/test sets. |
| **Statistics** | **Cherry Picking** | Reporting only the "significant" result from multiple uncorrected trials. |


## Installation

```bash
pip install demyst

# Or from source
git clone https://github.com/demyst/demyst.git
cd demyst
pip install -e .
```

## 5-Minute Setup

1. **Install**: `pip install demyst`
2. **Check your code**: `demyst analyze ./src`
3. **Add pre-commit**: Copy [`examples/configs/.pre-commit-config.minimal.yaml`](examples/configs/.pre-commit-config.minimal.yaml)
4. **Add CI**: Copy [`examples/configs/demyst-ci.yml`](examples/configs/demyst-ci.yml) to `.github/workflows/`

See the [**Quick Start Guide**](docs/quickstart.md) for the full walkthrough, or try the [**Interactive Notebook**](notebooks/quickstart.ipynb).

## Quick Start

```bash
# Run a Demyst Check
demyst analyze your_code.py
demyst analyze ./src/

# Individual checks
demyst mirage model.py           # Detect variance-destroying operations
demyst leakage train.py          # Detect train/test data leakage
demyst hypothesis stats.py       # Check statistical validity
demyst units physics.py          # Check dimensional consistency
demyst tensor network.py         # Check deep learning integrity

# Auto-fix mirages
demyst mirage model.py --fix
demyst mirage model.py --fix --dry-run  # Preview changes

# Generate Integrity Certificate (New in v1.2.0)
demyst report model.py --cert    # Creates signed integrity_certificate.json

# Run Red Team Benchmark
demyst red-team                  # Prove Demyst catches 100% of synthetic bugs

# CI/CD mode
demyst ci . --strict

# Generate LaTeX methodology
demyst paper model.py -o methodology.tex
```

## Mirage Detector Guide

- **Purpose**: Spots "computational mirages"—reductions (`mean`, `sum`, `argmax`, `argmin`) that erase variance on array-like data.
- **Coverage**: Tracks inline arrays, unknown variables (conservatively), and chained creators (`np.ones`, `np.cumsum`, `np.random.*`, 80+ numpy array builders). Method calls with extra args and nested reductions are also caught.
- **Run it**: `demyst mirage your_code.py` or `demyst mirage src/` to scan recursively.
- **Auto-fix**: `demyst mirage your_code.py --fix` rewrites dangerous reductions to `VariationTensor(...).collapse(...)` so you keep variance metadata.
- **Signal vs. noise**: If you already compute `std`/`var` within ~10 lines of the same data, Demyst suppresses the warning; otherwise it blocks on high-confidence mirages.

Example:

```python
import numpy as np

def analyze(scores):
    # Inline + chained creators are detected
    avg = np.mean(np.ones(100))
    # Method calls with args are detected too
    center = scores.mean(axis=0)
    return avg + center
```

Run `demyst mirage analyze.py` to flag both reductions and guide a safe rewrite.

## Real-World Examples: Where Mirages Cause Harm

These are documented cases where `np.mean()` and similar aggregations have hidden critical information. Demyst detects all of them.

### 1. Anscombe's Quartet (1973)
Four datasets with **identical means (7.5)** but completely different patterns: linear, quadratic, outlier, and leverage point.

```python
y1 = np.array([8.04, 6.95, 7.58, 8.81, 8.33, 9.96, 7.24, 4.26, 10.84, 4.82, 5.68])
y3 = np.array([7.46, 6.77, 12.74, 7.11, 7.81, 8.84, 6.08, 5.39, 8.15, 6.42, 5.73])
np.mean(y1)  # 7.50 - linear relationship
np.mean(y3)  # 7.50 - but there's an outlier at 12.74!
```

### 2. Simpson's Paradox (UC Berkeley 1973)
Aggregated data showed 44% male vs 35% female admission. But stratified by department, **women were MORE likely admitted** in 4/6 departments.

```python
overall_rate = np.mean(np.concatenate([dept_a, dept_f]))  # Hides confounding
```

### 3. Fat Tails in Finance
Average daily S&P return looks benign (~0.04%), but this hides:
- Black Monday 1987: **-22.6% in one day** (25-sigma event under normal distribution)
- 2008 crash, 2020 crash, flash crashes

```python
avg_return = np.mean(all_returns)  # ~0.03% - seems safe, but hides -22.6% crash
```

### 4. Climate Extremes
Average temperature rise of +2C hides a **5-10x increase in deadly heat days** (>35C).

```python
baseline_mean = np.mean(baseline_temps)  # 20C
future_mean = np.mean(future_temps)      # 22C - only +2C, seems mild
# But extreme heat days: 2 -> 15 (hidden by the average)
```

### 5. Outlier Masking
Multiple outliers **mask each other** by pulling the mean toward them, causing Grubbs' test to fail.

```python
all_data = np.array([10.2, 10.5, 9.8, 10.1, 25.0, 28.0])  # Two outliers
mean_val = np.mean(all_data)  # ~15.6 - pulled toward outliers
# Z-score test now FAILS to detect outliers (they corrupted the statistics)
```

Run the full example: `demyst mirage examples/real_world_mirages.py`

## The Swarm Collapse Problem (Nov 2025)

Imagine a swarm of 1,000 AI agents:
- **999 Agents**: Perfectly aligned (Score 1.0)
- **1 Agent**: Rogue/Jailbroken (Score 0.0)

Standard analysis using `np.mean()` gives a score of **0.999**. You deploy, and the rogue agent destroys the system.

**Demyst** detects this "computational mirage"—the loss of critical variance information—and prevents the catastrophe.

## Architecture



Demyst leverages **Abstract Syntax Tree (AST) parsing** for deep, semantic code analysis, ensuring it operates as a sophisticated code analysis tool rather than a "dumb" linter relying solely on regex.



```

demyst/

├── engine/

│   ├── mirage_detector.py        # **AST visitor** that flags destructive ops (critical for semantic analysis)

│   ├── variation_tensor.py       # Information-preserving data structure

│   ├── variation_transformer.py  # AST transformer for auto-fix

│   └── transpiler.py             # Auto-rewrites code

├── guards/

│   ├── tensor_guard.py           # Deep learning integrity

│   ├── leakage_hunter.py         # Data leakage detection

│   ├── hypothesis_guard.py       # Statistical validity (anti-p-hacking)

│   └── unit_guard.py             # Dimensional analysis

├── integrations/

│   ├── ci_enforcer.py            # CI/CD integration

│   ├── torch_hooks.py            # PyTorch integration

│   ├── jax_hooks.py              # JAX integration

│   └── experiment_trackers.py    # WandB/MLflow integration

├── mcp.py                        # **MCP Server** for AI Agents (Cursor, Claude)

├── red_team.py                   # **Red Team Benchmark** suite

├── generators/

│   ├── paper_generator.py        # LaTeX methodology generator

│   └── report_generator.py       # Integrity reports

└── config/

    └── manager.py                # Configuration management

```

## Configuration

Create `.demystrc.yaml` in your project root:

```yaml
profile: default  # Or: biology, physics, chemistry, neuroscience, climate, economics

rules:
  mirage:
    enabled: true
    severity: critical
  leakage:
    enabled: true
    severity: critical
  hypothesis:
    enabled: true
    severity: warning
  unit:
    enabled: true
    severity: warning
  tensor:
    enabled: true
    severity: critical

ignore_patterns:
  - "**/test_*"
  - "**/tests/**"
```

## CI/CD Integration

### GitHub Actions

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

### Pre-commit

```yaml
repos:
  - repo: https://github.com/demyst/demyst
    rev: v1.2.0
    hooks:
      - id: demyst
      # Or individual hooks:
      # - id: demyst-mirage
      # - id: demyst-leakage
      # - id: demyst-hypothesis
      # - id: demyst-tensor
      # - id: demyst-units
```

See [`examples/configs/`](examples/configs/) for ready-made configuration templates.

## Programmatic Usage

```python
from demyst import TensorGuard, LeakageHunter, HypothesisGuard, UnitGuard

with open('model.py', 'r') as f:
    source = f.read()

# Run individual guards
tensor_result = TensorGuard().analyze(source)
leakage_result = LeakageHunter().analyze(source)
hypothesis_result = HypothesisGuard().analyze_code(source)
unit_result = UnitGuard().analyze(source)

# Check for critical issues
if leakage_result['summary']['critical_count'] > 0:
    print("DATA LEAKAGE DETECTED - Results are invalid!")
```

## The Philosophical Bet

**Is a 10x slower but 1000x more correct computation acceptable?**

Demyst bets yes. We are moving from "fast but wrong" to "principled and preserved."

This aligns with the broader movement toward **self-verifiable AI reasoning**—systems that can prove their outputs are trustworthy, not just plausible. Whether in mathematical proofs (DeepSeek-Math-V2) or scientific code (Demyst), the goal is the same: **process integrity over outcome accuracy**.

## Related Work

- [DeepSeek-Math-V2: Towards Self-Verifiable Mathematical Reasoning](https://github.com/deepseek-ai/DeepSeek-Math-V2) - Self-verification in mathematical proofs
- [Uncertainty Quantification in ML](https://arxiv.org/abs/2107.03342) - Preserving uncertainty in predictions
- [Reproducibility Crisis in Science](https://www.nature.com/articles/533452a) - Why methodology verification matters

## Academic References

The mirage detection in Demyst is grounded in documented statistical phenomena:

| Phenomenon | Year | Key Finding | Reference |
|------------|------|-------------|-----------|
| **Anscombe's Quartet** | 1973 | Four datasets with identical summary statistics but different distributions | [Anscombe, F.J. (1973)](https://en.wikipedia.org/wiki/Anscombe%27s_quartet) |
| **Simpson's Paradox** | 1975 | Trends reverse when data is aggregated | [UC Berkeley Study (1975)](https://discovery.cs.illinois.edu/dataset/berkeley/) |
| **Fat Tails in Finance** | 1963 | Mandelbrot showed returns are not normally distributed | [Mandelbrot (1963)](https://en.wikipedia.org/wiki/Fat-tailed_distribution) |
| **Outlier Masking** | - | Multiple outliers corrupt mean/std, hiding each other | [GraphPad FAQ](https://www.graphpad.com/support/faq/masking-in-outlier-detection-why-it-can-be-harder-to-detect-two-outliers-than-one/) |
| **Data Leakage** | 2020+ | Preprocessing before split invalidates ML benchmarks | [scikit-learn #24390](https://github.com/scikit-learn/scikit-learn/issues/24390) |
| **Retraction Statistics** | 2017 | 18.9% of retractions involved analytical/computational errors | [PMC5395722](https://pmc.ncbi.nlm.nih.gov/articles/PMC5395722/) |

## License

MIT License - See [LICENSE](LICENSE) for details.

## Resources

- [**Quick Start Guide**](docs/quickstart.md) - Get started in 5 minutes
- [**Interactive Notebook**](notebooks/quickstart.ipynb) - Explore Demyst interactively
- [**Configuration Templates**](examples/configs/) - Ready-to-use configs for pre-commit, CI, and more
- [**Example Files**](examples/) - See what Demyst catches
- [**Full Documentation**](docs/usage.md) - Complete reference

## Contributing

We welcome contributions! See [docs/usage.md](docs/usage.md) for development setup.

---

*"The first principle is that you must not fool yourself—and you are the easiest person to fool."* - Richard Feynman
