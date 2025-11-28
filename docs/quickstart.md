# Demyst Quick Start

Get scientific integrity checks running in **5 minutes**.

---

## 1. Install (30 seconds)

```bash
pip install demyst
```

Verify installation:
```bash
demyst --version
# Output: demyst 1.2.0
```

---

## 2. Your First Check (1 minute)

Run Demyst on any Python file:

```bash
demyst analyze your_script.py
```

Or analyze an entire directory:

```bash
demyst analyze ./src
```

**What you'll see:**
- Computational mirages (mean/sum hiding variance)
- Data leakage (test data in training)
- P-hacking (uncorrected multiple testing)
- Unit mismatches (adding incompatible dimensions)
- Deep learning issues (gradient death, batch norm)

---

## 3. Try the Examples

Demyst includes example files that demonstrate each type of issue:

```bash
# See the Swarm Collapse problem (computational mirage)
demyst mirage examples/swarm_collapse.py

# Detect data leakage
demyst leakage examples/ml_data_leakage.py

# Find p-hacking
demyst hypothesis examples/biology_gene_expression.py

# Check unit/dimension errors
demyst units examples/physics_kinematics.py

# Check deep learning integrity
demyst tensor examples/deep_learning_gradient_death.py
```

---

## 4. Add Pre-commit Hooks (2 minutes)

Automatically check code before every commit.

**Step 1:** Create `.pre-commit-config.yaml` in your project root:

```yaml
repos:
  - repo: https://github.com/demyst/demyst
    rev: v1.2.0
    hooks:
      - id: demyst
```

Or copy the ready-made config:
```bash
cp examples/configs/.pre-commit-config.minimal.yaml .pre-commit-config.yaml
```

**Step 2:** Install the hooks:

```bash
pip install pre-commit
pre-commit install
```

Now every `git commit` will automatically run Demyst checks.

---

## 5. Add to CI/CD (1 minute)

**GitHub Actions:**

Copy the workflow file:
```bash
mkdir -p .github/workflows
cp examples/configs/demyst-ci.yml .github/workflows/demyst.yml
```

Or create `.github/workflows/demyst.yml`:

```yaml
name: Demyst Scientific Integrity

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
      - run: demyst ci .
```

---

## 6. Configure for Your Domain (Optional)

Create `.demystrc.yaml` for custom settings:

```yaml
profile: default  # Or: physics, biology, chemistry, neuroscience, economics

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
    severity: warning

ignore_patterns:
  - "**/test_*"
  - "**/tests/**"
```

See `examples/configs/` for ready-made configurations:
- `.demystrc.yaml` - Default configuration
- `.demystrc.strict.yaml` - Strict mode for CI/publishing
- `.demystrc.ml.yaml` - Optimized for ML projects

---

## What Demyst Catches

| Issue | Example | Impact |
|-------|---------|--------|
| **Computational Mirage** | `np.mean(scores)` hides outliers | Wrong decisions based on misleading metrics |
| **Data Leakage** | `fit_transform()` before split | Inflated accuracy, results don't replicate |
| **P-Hacking** | 100 tests at p<0.05 | ~5 false positives expected |
| **Unit Mismatch** | `distance + time` | Nonsensical physics |
| **Gradient Death** | 10-layer Sigmoid network | Model stops learning |

---

## CLI Commands Reference

```bash
demyst analyze <path>     # Run all checks
demyst mirage <file>      # Detect computational mirages
demyst leakage <file>     # Detect data leakage
demyst hypothesis <file>  # Check statistical validity
demyst units <file>       # Check dimensional consistency
demyst tensor <file>      # Check deep learning integrity
demyst ci <path>          # CI mode (exit codes for automation)
demyst fix <path>         # Auto-fix detected issues
demyst report <path>      # Generate integrity report
demyst paper <file>       # Generate LaTeX methodology section
```

Output formats: `--format text|markdown|json`

---

## Next Steps

- **Full documentation:** [docs/usage.md](usage.md)
- **Example files:** [examples/](../examples/)
- **Configuration templates:** [examples/configs/](../examples/configs/)
- **Interactive notebook:** [notebooks/quickstart.ipynb](../notebooks/quickstart.ipynb)

---

## Getting Help

- Issues: https://github.com/demyst/demyst/issues
- Documentation: https://github.com/demyst/demyst/docs/
