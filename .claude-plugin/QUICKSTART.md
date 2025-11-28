# Demyst Quick Start Guide

Get scientific integrity checking in 60 seconds.

## Step 1: Verify Installation

```bash
# Check demyst is available
demyst --version

# If not installed:
pip install demyst
```

## Step 2: Your First Check

Save this buggy code as `test_leakage.py`:

```python
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

# Generate data
X = np.random.randn(1000, 10)
y = (X[:, 0] > 0).astype(int)

# BUG: Preprocessing BEFORE split (data leakage!)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Split after preprocessing
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2)

# Train and evaluate
model = LogisticRegression()
model.fit(X_train, y_train)
print(f"Test accuracy: {model.score(X_test, y_test):.3f}")  # Inflated!
```

Run demyst:

```bash
demyst analyze test_leakage.py
```

**Expected output:**
```
🔓 CRITICAL: Data Leakage Detected
   Line 12: fit_transform() called before train_test_split()
   Impact: Test metrics are unreliable (inflated by ~5-15%)
   Fix: Split data first, then fit scaler on training data only
```

## Step 3: Fix the Bug

The correct version:

```python
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

# Generate data
X = np.random.randn(1000, 10)
y = (X[:, 0] > 0).astype(int)

# CORRECT: Split FIRST
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Then preprocess (fit only on train!)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)  # transform only, no fit!

# Train and evaluate
model = LogisticRegression()
model.fit(X_train_scaled, y_train)
print(f"Test accuracy: {model.score(X_test_scaled, y_test):.3f}")  # Honest!
```

## Step 4: Try the MCP Tools

In Claude Code, ask:

> "Use mcp__demyst__analyze_all to check this code: [paste code]"

Or use slash commands:

> `/demyst test_leakage.py`

## Step 5: Enable Proactive Checking

The plugin automatically checks Python files after you edit them. Just write code normally - demyst warns you about CRITICAL issues.

## Common Commands

| Task | Command |
|------|---------|
| Check a file | `demyst analyze model.py` |
| Check a directory | `demyst analyze ./src` |
| Auto-fix mirages | `demyst mirage model.py --fix` |
| Generate report | `demyst report model.py` |
| CI mode (strict) | `demyst ci . --strict` |

## MCP Tools Reference

| Tool | When to Use |
|------|-------------|
| `analyze_all` | Full check (recommended for most cases) |
| `detect_mirage` | Checking aggregation operations |
| `detect_leakage` | Checking ML pipelines |
| `check_hypothesis` | Checking statistical code |
| `check_tensor` | Checking PyTorch/JAX code |
| `check_units` | Checking physics/engineering code |
| `fix_mirages` | Auto-fixing variance issues |
| `generate_report` | Creating documentation |

## Next Steps

1. **Read the Hall of Shame** in README.md for common mistakes
2. **Configure profiles** for your domain (physics, biology, etc.)
3. **Add to CI/CD** for automatic checking
4. **Share with your team** - reproducible science starts with integrity

---

*Questions? Issues? [Open an issue on GitHub](https://github.com/Hmbown/demyst/issues)*
