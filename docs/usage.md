# Demyst Usage Guide

Demyst is a Scientific Integrity Platform that helps detect and prevent common errors in machine learning and data science code.

## Installation

```bash
# From PyPI (when released)
pip install demyst

# From source
git clone https://github.com/demyst/demyst.git
cd demyst
pip install -e .

# With development dependencies
pip install -e ".[dev]"
```

## Quick Start

### Run All Checks

```bash
demyst analyze your_code.py
demyst analyze ./src/
```

### Individual Checks

```bash
# Detect computational mirages (variance-destroying operations)
demyst mirage model.py

# Detect train/test data leakage
demyst leakage train.py

# Check statistical validity (anti-p-hacking)
demyst hypothesis stats.py

# Check dimensional consistency
demyst units physics.py

# Check deep learning integrity
demyst tensor network.py
```

## Commands Reference

### `demyst analyze`

Run all integrity checks on a file or directory.

```bash
demyst analyze <path> [--format markdown|json|text] [--config CONFIG]
```

**Options:**
- `--format, -f`: Output format (markdown, json, text)
- `--config, -c`: Path to configuration file

### `demyst mirage`

Detect computational mirages - operations that destroy variance/distribution information.

```bash
demyst mirage <file> [--fix] [--output FILE] [--diff] [--dry-run]
```

**Options:**
- `--fix`: Auto-fix detected mirages using the transpiler
- `--output, -o`: Output file for fixed code
- `--diff`: Show diff of proposed changes
- `--dry-run`: Show what would be done without making changes

**Example:**
```bash
# Detect mirages
demyst mirage model.py

# Auto-fix mirages
demyst mirage model.py --fix

# Preview changes
demyst mirage model.py --fix --dry-run
```

### `demyst leakage`

Detect train/test data leakage - the #1 error in machine learning.

```bash
demyst leakage <file>
```

**Detects:**
- Test data used in training
- Preprocessing before split (fit_transform leakage)
- Target leakage in cross-validation
- Hyperparameter tuning on test data

### `demyst hypothesis`

Check statistical validity and detect p-hacking patterns.

```bash
demyst hypothesis <file>
```

**Detects:**
- Multiple comparisons without correction
- Conditional reporting based on p-values
- Cherry-picking of results

**Correction methods supported:**
- Bonferroni correction
- Holm-Bonferroni step-down
- Benjamini-Hochberg FDR control

### `demyst units`

Check dimensional consistency and unit mismatches.

```bash
demyst units <file>
```

**Detects:**
- Adding incompatible dimensions (meters + seconds)
- Unit conversion errors
- Dimensionless assumptions that hide physical meaning

### `demyst tensor`

Check deep learning integrity for PyTorch and JAX code.

```bash
demyst tensor <file>
```

**Detects:**
- Gradient death chains (vanishing/exploding gradients)
- Normalization blindness (BatchNorm hiding distribution shifts)
- Reward hacking vulnerabilities in RL

### `demyst paper`

Generate LaTeX methodology section from code.

```bash
demyst paper <file> [--output FILE] [--title TITLE] [--style STYLE] [--full]
```

**Options:**
- `--output, -o`: Output file for LaTeX
- `--title, -t`: Section title
- `--style, -s`: Paper style (neurips, icml, iclr, arxiv)
- `--full`: Generate full paper template

### `demyst ci`

Run in CI/CD enforcement mode.

```bash
demyst ci [path] [--strict] [--config CONFIG]
```

**Options:**
- `--strict`: Fail on warnings (not just critical issues)
- `--config, -c`: Path to configuration file

## Configuration

Create a `.demystrc.yaml` file in your project root:

```yaml
# Domain profile (default, biology, physics, neuroscience, climate, economics)
profile: default

# Rule configuration
rules:
  mirage:
    enabled: true
    severity: critical
    exclude: []
  tensor:
    enabled: true
    severity: critical
    exclude: []
  leakage:
    enabled: true
    severity: critical
    exclude: []
  hypothesis:
    enabled: true
    severity: warning
    exclude: []
  unit:
    enabled: true
    severity: warning
    exclude: []

# Files to ignore
ignore_patterns:
  - "**/test_*"
  - "**/*_test.py"
  - "**/tests/**"
  - "**/.git/**"
  - "**/venv/**"
```

## Pre-commit Integration

Add to your `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/demyst/demyst
    rev: v1.0.0
    hooks:
      - id: demyst
        # Or use individual hooks:
        # - id: demyst-mirage
        # - id: demyst-leakage
```

## GitHub Actions Integration

Add to `.github/workflows/demyst.yml`:

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

## Programmatic Usage

```python
from demyst import TensorGuard, LeakageHunter, HypothesisGuard, UnitGuard

# Read your code
with open('model.py', 'r') as f:
    source = f.read()

# Run individual guards
tensor_result = TensorGuard().analyze(source)
leakage_result = LeakageHunter().analyze(source)
hypothesis_result = HypothesisGuard().analyze_code(source)
unit_result = UnitGuard().analyze(source)

# Check for issues
if tensor_result['summary']['critical_issues'] > 0:
    print("Critical tensor integrity issues found!")

if leakage_result['summary']['critical_count'] > 0:
    print("Data leakage detected!")
```

## Debug Mode

Enable debug output for troubleshooting:

```bash
# Using CLI flag
demyst analyze model.py --debug

# Using environment variable
DEMYST_DEBUG=1 demyst analyze model.py
```

## Verbose Mode

Enable verbose output for more information:

```bash
demyst analyze model.py --verbose
```
