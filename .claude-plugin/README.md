# Demyst - Scientific Integrity for Claude Code

> **"Good Code is Good Science"** - Demyst ensures your ML code means what you think it means.

[![Demyst](https://img.shields.io/badge/demyst-scientific%20integrity-blue)](https://github.com/Hmbown/demyst)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MCP Tools](https://img.shields.io/badge/MCP%20Tools-9-purple)](.)

## What is Demyst?

Demyst is a **scientific integrity linter** for ML and data science code. It catches errors that are:
- ✅ Syntactically valid
- ❌ Scientifically wrong

These are the bugs that pass all tests but make your research unreliable.

## The 5 Guards

| Guard | Severity | What It Catches |
|-------|----------|-----------------|
| 🌀 **Mirage** | CRITICAL | `mean()` hiding catastrophic outliers |
| 🔓 **Leakage** | CRITICAL | Test data contaminating training |
| 📊 **Hypothesis** | WARNING | P-hacking and multiple comparisons |
| 🧠 **Tensor** | WARNING | Vanishing gradients, reward hacking |
| 📐 **Units** | WARNING | Adding meters to seconds |

## Quick Start

### Via MCP Tools (Recommended)

The plugin exposes 9 MCP tools. Use them directly:

```
mcp__demyst__analyze_all       # Run all guards
mcp__demyst__detect_mirage     # Check for variance destruction
mcp__demyst__detect_leakage    # Check for data leakage
mcp__demyst__check_hypothesis  # Check statistical validity
mcp__demyst__check_tensor      # Check deep learning integrity
mcp__demyst__check_units       # Check dimensional consistency
mcp__demyst__fix_mirages       # Auto-fix mirage violations
mcp__demyst__generate_report   # Generate integrity report
mcp__demyst__sign_verification # Create cryptographic certificate
```

### Via Slash Commands

```
/demyst              # Full analysis of current file
/demyst-fix          # Auto-fix mirages
/demyst-report       # Generate detailed report
```

### Via CLI

```bash
demyst analyze model.py        # Run all checks
demyst mirage model.py --fix   # Auto-fix mirages
demyst report model.py         # Generate report
```

## Proactive Checking

This plugin includes a **PostToolUse hook** that automatically checks Python files after you write or edit them. It only reports CRITICAL issues to avoid noise.

Example output:
```
**Demyst Warning** (line 15): fit_transform() before train_test_split() - test data leaks into training
Suggestion: Split data FIRST, then fit preprocessing on train only.
```

## Hall of Shame: Common Mistakes

### 🌀 The Swarm Collapse (Mirage)

```python
# 999 good agents, 1 catastrophic failure
scores = [1.0] * 999 + [0.0]
print(np.mean(scores))  # 0.999 - "Everything is fine!"
# Reality: One agent caused total system failure
```

**Fix:** Track both mean AND variance, or use VariationTensor.

---

### 🔓 The Preprocessing Leak (Leakage)

```python
# WRONG - This is in 90% of Kaggle notebooks!
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)  # ← Fitted on ALL data
X_train, X_test = train_test_split(X_scaled)

# Your test accuracy is a lie. The scaler "knows" test statistics.
```

**Fix:** Split first, fit on train only.

---

### 📊 The P-Hacking Trap (Hypothesis)

```python
# Testing 20 features at p<0.05
# Expected false positives: 1 (even with random data!)
for feature in features:
    if ttest(feature, target).pvalue < 0.05:
        print(f"{feature} is significant!")  # Is it though?
```

**Fix:** Apply Bonferroni correction: `alpha = 0.05 / num_tests`

---

### 🧠 The Gradient Graveyard (Tensor)

```python
# Deep sigmoid chain = dead gradients
x = torch.sigmoid(x)
x = torch.sigmoid(x)
x = torch.sigmoid(x)  # Gradient ≈ 0. Learning stops.
```

**Fix:** Use residual connections or ReLU variants.

---

### 📐 The Unit Mismatch (Units)

```python
distance = 100  # meters
time = 10       # seconds
result = distance + time  # ??? What unit is this?
```

**Fix:** Demyst tracks dimensions and catches incompatible operations.

## Example Workflows

### Before Submitting a Paper

```
1. /demyst model.py              # Check for issues
2. /demyst-fix model.py          # Auto-fix what's possible
3. /demyst-report model.py       # Generate methodology section
4. Request certificate for proof of verification
```

### In CI/CD Pipeline

```yaml
- name: Scientific Integrity Check
  run: demyst ci . --strict
```

### Code Review Checklist

- [ ] No mirages (variance-destroying operations)
- [ ] No leakage (preprocessing after split)
- [ ] Multiple comparisons corrected
- [ ] Gradient flow preserved
- [ ] Units consistent

## Configuration

Create `.demystrc.yaml` in your project root:

```yaml
profile: default  # or: physics, biology, chemistry, climate

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
  tensor:
    enabled: true
    severity: warning
  unit:
    enabled: true
    severity: warning
```

## MCP Server Setup

For use with Cursor, Claude Desktop, or other MCP clients:

```json
{
  "mcpServers": {
    "demyst": {
      "command": "python",
      "args": ["-m", "demyst.mcp"]
    }
  }
}
```

## Why Demyst?

| Traditional Linters | Demyst |
|---------------------|--------|
| Check syntax | Check scientific correctness |
| Find unused variables | Find data leakage |
| Style violations | Statistical validity violations |
| Works on all code | Specialized for ML/science |

**Demyst catches the bugs that matter for science.**

## License

MIT - Use freely in research and commercial projects.

## Links

- [GitHub Repository](https://github.com/Hmbown/demyst)
- [Documentation](https://demyst.readthedocs.io)
- [PyPI Package](https://pypi.org/project/demyst)

---

*Built with ❤️ for reproducible science*
