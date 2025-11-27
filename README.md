# Scilint: The Scientific Integrity Platform

[![Scilint: Verified](https://img.shields.io/badge/Scilint-Verified-purple)](https://github.com/scilint/scilint)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> "Science is the belief in the ignorance of experts." - Richard Feynman
>
> "Correct answers don't guarantee correct reasoning." - DeepSeek-Math-V2

**Scilint** is a **Scientific Integrity Platform** that helps researchers, AI agents, and data scientists ensure their code lives up to the rigor of their ideas.

## The Core Problem: Self-Verifiable Scientific Reasoning

In the age of AI and rapid prototyping, we face a fundamental epistemological challenge:

**How do we know our computation is trustworthy, not just its output?**

This mirrors the insight from recent work on [self-verifiable mathematical reasoning](https://github.com/deepseek-ai/DeepSeek-Math-V2) (DeepSeek-Math-V2, 2025): correct answers don't guarantee correct reasoning. A model can produce the right numerical result through flawed logic, and a scientific computation can produce plausible metrics through statistically invalid processes.

Scilint attacks this problem from the code verification angle:

| Problem | Mathematical Proofs | Scientific Code |
|---------|---------------------|-----------------|
| **The Mirage** | Right answer, wrong proof | Good metrics, invalid methodology |
| **Solution** | Verify proof steps | Verify computation integrity |
| **Approach** | Self-verifiable reasoning | Information-preserving transforms |

See the [Full Demonstration](docs/demonstration.md) for detailed examples of Scilint in action.


## What Scilint Detects

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

# Scilint recommends: Bonferroni, Holm-Bonferroni, or Benjamini-Hochberg correction
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

# Scilint detects: "Cannot add quantities with dimensions [L] and [T]"
```

## What Scilint Catches

Scilint is designed to catch **scientific logic errors** that standard linters miss.

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
# From source
git clone https://github.com/scilint/scilint.git
cd scilint
pip install -e .

# With development dependencies
pip install -e ".[dev]"
```

## Quick Start

```bash
# Run all integrity checks
scilint analyze your_code.py
scilint analyze ./src/

# Individual checks
scilint mirage model.py           # Detect variance-destroying operations
scilint leakage train.py          # Detect train/test data leakage
scilint hypothesis stats.py       # Check statistical validity
scilint units physics.py          # Check dimensional consistency
scilint tensor network.py         # Check deep learning integrity

# Auto-fix mirages
scilint mirage model.py --fix
scilint mirage model.py --fix --dry-run  # Preview changes

# CI/CD mode
scilint ci . --strict

# Generate LaTeX methodology
scilint paper model.py -o methodology.tex
```

## The Swarm Collapse Problem (Nov 2025)

Imagine a swarm of 1,000 AI agents:
- **999 Agents**: Perfectly aligned (Score 1.0)
- **1 Agent**: Rogue/Jailbroken (Score 0.0)

Standard analysis using `np.mean()` gives a score of **0.999**. You deploy, and the rogue agent destroys the system.

**Scilint** detects this "computational mirage"—the loss of critical variance information—and prevents the catastrophe.

## Architecture

```
scilint/
├── engine/
│   ├── mirage_detector.py        # AST visitor that flags destructive ops
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
├── generators/
│   ├── paper_generator.py        # LaTeX methodology generator
│   └── report_generator.py       # Integrity reports
└── config/
    └── manager.py                # Configuration management
```

## Configuration

Create `.scilintrc.yaml` in your project root:

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
name: Scilint
on: [push, pull_request]

jobs:
  scilint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install scilint
      - run: scilint ci . --strict
```

### Pre-commit

```yaml
repos:
  - repo: https://github.com/scilint/scilint
    rev: v1.0.0
    hooks:
      - id: scilint
      # Or individual hooks:
      # - id: scilint-mirage
      # - id: scilint-leakage
```

## Programmatic Usage

```python
from scilint import TensorGuard, LeakageHunter, HypothesisGuard, UnitGuard

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

Scilint bets yes. We are moving from "fast but wrong" to "principled and preserved."

This aligns with the broader movement toward **self-verifiable AI reasoning**—systems that can prove their outputs are trustworthy, not just plausible. Whether in mathematical proofs (DeepSeek-Math-V2) or scientific code (Scilint), the goal is the same: **process integrity over outcome accuracy**.

## Related Work

- [DeepSeek-Math-V2: Towards Self-Verifiable Mathematical Reasoning](https://github.com/deepseek-ai/DeepSeek-Math-V2) - Self-verification in mathematical proofs
- [Uncertainty Quantification in ML](https://arxiv.org/abs/2107.03342) - Preserving uncertainty in predictions
- [Reproducibility Crisis in Science](https://www.nature.com/articles/533452a) - Why methodology verification matters

## License

MIT License - See [LICENSE](LICENSE) for details.

## Contributing

We welcome contributions! See [docs/usage.md](docs/usage.md) for development setup.

---

*"The first principle is that you must not fool yourself—and you are the easiest person to fool."* - Richard Feynman
