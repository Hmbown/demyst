# Scilint Handoff: Domain-Specific Examples Needed

## Status

Scilint v1.0 is feature-complete and passes core tests. The following tasks remain for final polish:

### Ready for Launch
- [x] CLI with all commands working
- [x] All guards functional (TensorGuard, LeakageHunter, HypothesisGuard, UnitGuard)
- [x] Auto-fix via transpiler (`scilint mirage --fix`)
- [x] Pre-commit hooks configured
- [x] CI/CD integration
- [x] Documentation (README, docs/usage.md)
- [x] Edge case tests (60+ tests passing)

### Domain-Specific Examples Needed

Create realistic, runnable examples in `examples/` folder for each domain:

---

## 1. Biology Examples (`examples/biology/`)

### Gene Expression Analysis (`gene_expression.py`)
```python
# Example issues to demonstrate:
# - Data leakage: Normalizing gene expression data before train/test split
# - P-hacking: Testing 20,000 genes without multiple comparison correction
# - Computational mirage: Averaging across replicates hides batch effects

# Include:
# - RNA-seq data simulation
# - Differential expression analysis
# - Scilint detection of issues
```

### Drug Response Prediction (`drug_response.py`)
```python
# Example issues:
# - Data leakage: Feature selection on full dataset
# - Reward hacking: Optimizing for average AUC hides cell-line-specific failures
```

### CRISPR Screen Analysis (`crispr_screen.py`)
```python
# Example issues:
# - Multiple testing: Thousands of guide RNAs tested
# - Distribution collapse: Aggregating guide-level to gene-level scores
```

---

## 2. Physics Examples (`examples/physics/`)

### Particle Physics (`particle_collision.py`)
```python
# Example issues:
# - Dimensional analysis: Energy vs momentum units
# - Variance destruction: Binning continuous distributions
# - Look-elsewhere effect (p-hacking in signal searches)
```

### Quantum Computing (`quantum_simulation.py`)
```python
# Example issues:
# - Gradient death: Deep variational quantum circuits
# - Unit errors: Mixing natural units with SI
```

### Climate Modeling (`climate_analysis.py`)
```python
# Example issues:
# - Temporal leakage: Future data in training
# - Spatial aggregation destroying local signals
# - Unit mismatches in temperature/energy calculations
```

---

## 3. Chemistry Examples (`examples/chemistry/`)

### Molecular Property Prediction (`molecular_ml.py`)
```python
# Example issues:
# - Data leakage: Scaffold split vs random split
# - Dimensional analysis: Energy units in different contexts
```

### Reaction Yield Prediction (`reaction_yield.py`)
```python
# Example issues:
# - P-hacking: Testing many reaction conditions
# - Preprocessing leakage: StandardScaler on full dataset
```

### Materials Discovery (`materials_screening.py`)
```python
# Example issues:
# - Multiple testing across material candidates
# - Variance collapse in property aggregation
```

---

## 4. Neuroscience Examples (`examples/neuroscience/`)

### fMRI Analysis (`fmri_analysis.py`)
```python
# Example issues:
# - Voxel-wise multiple testing (thousands of voxels)
# - Temporal leakage in time-series classification
# - Circular analysis (double dipping)
```

### EEG/MEG Analysis (`eeg_analysis.py`)
```python
# Example issues:
# - Channel-wise multiple testing
# - Data leakage in cross-validation
```

---

## 5. Economics/Finance Examples (`examples/economics/`)

### Time Series Forecasting (`stock_prediction.py`)
```python
# Example issues:
# - Look-ahead bias (temporal leakage)
# - Multiple testing across trading strategies
```

### A/B Testing (`ab_testing.py`)
```python
# Example issues:
# - Early stopping (peeking)
# - Multiple comparison in segmentation analysis
```

---

## Implementation Guidelines

For each example:

1. **Create realistic synthetic data** (or use public datasets)
2. **Show the problematic code** with clear comments
3. **Run scilint to detect issues**
4. **Show the corrected code**
5. **Include a README explaining the scientific context**

### Example Structure
```
examples/
├── biology/
│   ├── README.md
│   ├── gene_expression.py
│   ├── drug_response.py
│   └── crispr_screen.py
├── physics/
│   ├── README.md
│   ├── particle_collision.py
│   └── climate_analysis.py
├── chemistry/
│   ├── README.md
│   └── molecular_ml.py
├── neuroscience/
│   ├── README.md
│   └── fmri_analysis.py
└── economics/
    ├── README.md
    └── ab_testing.py
```

---

## Testing Checklist

After adding examples, verify:

```bash
# Each example should run without errors
python examples/biology/gene_expression.py

# Each example should trigger scilint warnings
scilint analyze examples/biology/gene_expression.py

# The fix should work
scilint mirage examples/biology/gene_expression.py --fix --dry-run
```

---

## Philosophy Connection

Each example should reinforce the core insight shared with [DeepSeek-Math-V2](https://github.com/deepseek-ai/DeepSeek-Math-V2):

> "Correct answers don't guarantee correct reasoning."

In scientific code:
- A good accuracy score doesn't mean valid methodology
- A significant p-value doesn't mean rigorous statistics
- A converged model doesn't mean proper training

Scilint verifies the **process**, not just the **outcome**.

---

## Notes

- Pre-existing test failures are in optional integration tests (wandb/mlflow not installed)
- Core functionality is solid (60+ tests passing)
- Performance is good (<3s for typical files)
