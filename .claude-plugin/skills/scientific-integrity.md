---
description: |
  Use this skill when writing or reviewing ML/data science code to ensure scientific integrity.
  Activate when you see: numpy, pandas, sklearn, torch, tensorflow, statistical tests, data pipelines,
  neural networks, reward functions, physical quantities, or scientific computing code.
---

# Demyst Scientific Integrity Checker

You have access to **Demyst**, a scientific integrity linter that ensures your code means what you think it means. It detects issues that are scientifically incorrect but syntactically valid.

## The 5 Guards

### 1. Mirage Detection (CRITICAL)

**Problem:** Variance-destroying operations hide critical information.

**The Swarm Collapse Example:**
```python
# 999 agents score 1.0, but 1 rogue agent scores 0.0
scores = [1.0] * 999 + [0.0]
avg = np.mean(scores)  # Returns 0.999 - looks great!
# But the rogue agent caused a catastrophic failure you'll never see
```

**Red Flags:**
- `np.mean()`, `np.sum()` on high-variance data
- `argmax()`, `argmin()` without variance tracking
- Any aggregation without checking distribution shape

**CLI:** `demyst mirage <file.py>`
**MCP Tool:** `mcp__demyst__detect_mirage`

---

### 2. Data Leakage Detection (CRITICAL)

**Problem:** Test data contaminating training makes benchmarks unreliable.

**The Preprocessing Leak Example:**
```python
# WRONG - test data statistics leak into training
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)  # Fitted on ALL data including test!
X_train, X_test = train_test_split(X_scaled)

# CORRECT - fit only on training data
X_train, X_test = train_test_split(X)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)  # Fit on train only
X_test_scaled = scaler.transform(X_test)  # Transform test
```

**Red Flags:**
- `fit_transform()` before `train_test_split()`
- Target encoding before cross-validation
- Using test indices during training
- Hyperparameter tuning on test data

**CLI:** `demyst leakage <file.py>`
**MCP Tool:** `mcp__demyst__detect_leakage`

---

### 3. Hypothesis Guard (WARNING)

**Problem:** Multiple statistical tests inflate false positive rates (p-hacking).

**The Multiple Comparisons Problem:**
```python
# WRONG - 20 tests at p<0.05 means ~1 false positive expected
for feature in features:
    p = ttest(feature, target)
    if p < 0.05:  # Will find "significant" results by chance!
        print(f"{feature} is significant")

# CORRECT - apply Bonferroni correction
alpha = 0.05 / len(features)  # Corrected threshold
for feature in features:
    p = ttest(feature, target)
    if p < alpha:
        print(f"{feature} is significant")
```

**Red Flags:**
- Multiple t-tests/ANOVAs without correction
- Conditional logic on p-values (`if p < 0.05`)
- Reporting only significant results

**CLI:** `demyst hypothesis <file.py>`
**MCP Tool:** `mcp__demyst__check_hypothesis`

---

### 4. Unit Guard (WARNING)

**Problem:** Adding incompatible physical quantities is meaningless.

**The Dimensional Analysis Example:**
```python
# WRONG - adding meters to seconds
distance = 100  # meters
time = 10  # seconds
result = distance + time  # Meaningless! [L] + [T] = ???

# CORRECT - compute velocity
velocity = distance / time  # m/s - [L]/[T] = [L T^-1]
```

**Common Dimensions:**
- Length [L]: meters, feet, km
- Time [T]: seconds, hours
- Velocity [L T^-1]: m/s, km/h
- Force [M L T^-2]: Newtons

**CLI:** `demyst units <file.py>`
**MCP Tool:** `mcp__demyst__check_units`

---

### 5. Tensor Guard (WARNING)

**Problem:** Deep learning integrity issues that cause silent failures.

**Gradient Death Example:**
```python
# WRONG - deep sigmoid chains cause vanishing gradients
x = torch.sigmoid(x)
x = torch.sigmoid(x)
x = torch.sigmoid(x)  # Gradients approach 0

# CORRECT - use residual connections or different activations
x = x + torch.relu(self.layer(x))  # Skip connection preserves gradient flow
```

**Red Flags:**
- Deep chains of sigmoid/tanh without residuals
- `BatchNorm(track_running_stats=False)` - masks distribution shifts
- `mean(rewards)` in RL - hides catastrophic failures

**CLI:** `demyst tensor <file.py>`
**MCP Tool:** `mcp__demyst__check_tensor`

---

## How to Use Demyst

### Quick Check (Recommended)
```bash
demyst analyze <file.py>
```
Runs all 5 guards and reports issues.

### MCP Tools

Use these MCP tools for programmatic checking:

| Tool | Purpose |
|------|---------|
| `mcp__demyst__analyze_all` | Run all guards (recommended) |
| `mcp__demyst__detect_mirage` | Check for variance destruction |
| `mcp__demyst__detect_leakage` | Check for data leakage |
| `mcp__demyst__check_hypothesis` | Check statistical validity |
| `mcp__demyst__check_tensor` | Check deep learning integrity |
| `mcp__demyst__check_units` | Check dimensional consistency |
| `mcp__demyst__fix_mirages` | Auto-fix mirage violations |
| `mcp__demyst__generate_report` | Generate integrity report |

### Auto-Fix
```bash
demyst fix <file.py>  # Fix mirages automatically
```

### Generate Report
```bash
demyst report <file.py>  # Markdown report for docs/PRs
```

---

## When to Check

**Always check when:**
- Writing ML training pipelines
- Implementing data preprocessing
- Performing statistical analysis
- Working with physical quantities
- Building neural network architectures
- Implementing RL reward functions

**Severity Levels:**
- **CRITICAL** (Mirage, Leakage): These make results fundamentally unreliable
- **WARNING** (Hypothesis, Tensor, Units): These may cause subtle issues

---

## Example Workflow

1. Write your ML code
2. Run `demyst analyze model.py`
3. Review CRITICAL issues first
4. Use `demyst fix model.py` to auto-fix mirages
5. Manually fix leakage issues
6. Generate report for documentation: `demyst report model.py`
