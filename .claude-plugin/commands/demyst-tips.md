---
description: Quick scientific integrity tips - cheat sheet for common issues
arguments:
  - name: topic
    description: Topic (leakage, mirage, stats, dl, units, or all)
    required: false
---

Show quick scientific integrity tips.

## Instructions

Based on the topic, show relevant tips:

### If topic is "leakage" or includes ML pipelines:

```
🔓 DATA LEAKAGE PREVENTION

DO:
✅ Split data BEFORE any preprocessing
✅ Fit scalers/encoders on train only
✅ Use sklearn Pipeline + cross_val_score
✅ Keep test set locked until final evaluation

DON'T:
❌ fit_transform() before train_test_split()
❌ Target encoding before cross-validation
❌ Using test indices during training
❌ Hyperparameter tuning on test set

Quick Check:
  demyst leakage <file.py>
```

### If topic is "mirage" or includes aggregations:

```
🌀 MIRAGE PREVENTION

DO:
✅ Track mean AND std/variance together
✅ Check distribution shape before aggregating
✅ Use anomaly detection for outliers
✅ Log individual values, not just aggregates

DON'T:
❌ np.mean() on potentially heavy-tailed data
❌ argmax/argmin without checking variance
❌ sum() when outliers could dominate

Quick Check:
  demyst mirage <file.py>
```

### If topic is "stats" or "phacking" or includes statistical tests:

```
📊 STATISTICAL VALIDITY

DO:
✅ Pre-register your hypothesis
✅ Apply Bonferroni: α_corrected = 0.05 / n_tests
✅ Report ALL tests, not just significant ones
✅ Use FDR correction for many tests

DON'T:
❌ Run many tests, report only p < 0.05
❌ Add more subjects until p < 0.05
❌ Change hypothesis after seeing data

Quick Check:
  demyst hypothesis <file.py>
```

### If topic is "dl" or "tensor" or includes neural networks:

```
🧠 DEEP LEARNING INTEGRITY

DO:
✅ Use residual connections in deep networks
✅ Monitor gradient magnitudes during training
✅ Track reward DISTRIBUTION in RL, not just mean
✅ Use LayerNorm or careful initialization

DON'T:
❌ Deep sigmoid/tanh chains without skip connections
❌ BatchNorm(track_running_stats=False) in production
❌ Only track mean(rewards) in RL

Quick Check:
  demyst tensor <file.py>
```

### If topic is "units" or includes physical quantities:

```
📐 DIMENSIONAL ANALYSIS

DO:
✅ Document units in variable names or comments
✅ Use pint or similar for unit tracking
✅ Check dimensional consistency manually

DON'T:
❌ Add quantities with different dimensions
❌ Compare meters to seconds
❌ Forget unit conversions

Quick Check:
  demyst units <file.py>
```

### If topic is "all" or not specified:

Show a summary card:

```
🔬 DEMYST QUICK REFERENCE

┌─────────────────────────────────────────────────┐
│  CRITICAL ISSUES (Fix immediately)              │
├─────────────────────────────────────────────────┤
│ 🔓 Leakage: Split BEFORE preprocessing          │
│ 🌀 Mirage:  Track variance, not just mean       │
├─────────────────────────────────────────────────┤
│  WARNING ISSUES (Should investigate)            │
├─────────────────────────────────────────────────┤
│ 📊 Stats:   Correct for multiple comparisons    │
│ 🧠 DL:      Add residuals to deep networks      │
│ 📐 Units:   Don't mix incompatible dimensions   │
└─────────────────────────────────────────────────┘

Commands:
  /demyst            Full analysis
  /demyst-fix        Auto-fix mirages
  /demyst-report     Generate report
  /demyst-challenge  Interactive practice

MCP Tools:
  mcp__demyst__analyze_all (recommended)
```
