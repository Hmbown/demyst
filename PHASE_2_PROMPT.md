# Scilint Phase 2: Universal Scientific Integrity Platform

## Context
You are an expert Scientific Software Architect. Scilint v1.0 has been built with:
- **TensorGuard**: Deep learning integrity (gradient death, normalization blindness, reward hacking)
- **LeakageHunter**: Taint analysis for train/test data leakage
- **HypothesisGuard**: Anti-p-hacking with Bonferroni/Holm/BH corrections
- **UnitGuard**: Dimensional analysis engine
- **CI/CD Enforcer**: GitHub Action with PR comments
- **Paper Generator**: LaTeX methodology from code

## Mission: Make Scilint Universally Adoptable
Expand Scilint to serve **ALL scientific disciplines** while maintaining the core philosophy: "Good Code is Good Science."

---

## Phase 2 Objectives

### 1. Domain-Specific Profiles (Priority: HIGH)
Create pluggable rule sets for different scientific domains:

```yaml
# .scilintrc.yaml
profile: physics  # or: biology, economics, climate, neuroscience
severity_override:
  unit_mismatch: error  # vs warning
custom_units:
  - name: electron_volt
    dimension: [2, 1, -2, 0, 0, 0, 0]  # Energy
```

**Domains to support:**
- **Physics**: Dimensional analysis, conservation laws, uncertainty propagation
- **Biology/Medicine**: Effect sizes, multiple testing corrections, survival analysis checks
- **Economics/Finance**: Autocorrelation checks, stationarity tests, lookahead bias
- **Climate Science**: Temporal leakage, spatial autocorrelation, ensemble handling
- **Neuroscience**: Multiple comparisons, circular analysis, double-dipping

### 2. Configuration System (Priority: HIGH)
Implement hierarchical configuration:

```
project/.scilintrc.yaml     # Project config
~/.config/scilint/config.yaml  # User config
/etc/scilint/config.yaml    # System config
```

Support:
- Rule enable/disable
- Severity customization
- Custom unit definitions
- Ignore patterns (files, lines, rules)
- Domain profile selection

### 3. Auto-Fix Mode (Priority: HIGH)
Implement automatic code fixes:

```bash
scilint fix model.py              # Fix all auto-fixable issues
scilint fix model.py --dry-run    # Show what would be fixed
scilint fix model.py --interactive  # Confirm each fix
```

Auto-fixable patterns:
- `np.mean(data)` → `VariationTensor(data).collapse('mean')`
- Missing Bonferroni correction → Insert `multipletests()` call
- Preprocessing before split → Reorder with Pipeline

### 4. IDE Integration (Priority: MEDIUM)
**VS Code Extension:**
- Real-time linting via LSP
- Inline issue highlighting
- Quick-fix code actions
- Hover documentation explaining WHY something is wrong

**Jupyter Integration:**
- Cell-level analysis
- Magic command: `%scilint`
- Pre-run checks before execution

### 5. Expanded Framework Support (Priority: MEDIUM)
Add support for:
- **TensorFlow/Keras**: Same checks as PyTorch
- **scikit-learn Pipelines**: Ensure correct cross-validation
- **Pandas**: DataFrame operation tracking
- **R interop**: Support for reticulate workflows
- **Julia**: Basic support via PyCall

### 6. Advanced Taint Analysis (Priority: MEDIUM)
Enhance LeakageHunter with:
- **Cross-file tracking**: Follow data across imports
- **Notebook cell ordering**: Detect out-of-order execution leakage
- **Database queries**: Track data from SQL sources
- **Feature stores**: Integrate with Feast, Tecton
- **Time-series specific**: Detect future data leakage in temporal splits

### 7. Reproducibility Validator (Priority: MEDIUM)
New guard: **ReproducibilityGuard**
- Detect non-deterministic operations without seed setting
- Check for hardware-dependent code (GPU race conditions)
- Validate environment pinning (requirements.txt completeness)
- Docker/container configuration analysis

### 8. Statistical Power Analysis (Priority: LOW)
Enhance HypothesisGuard:
- Pre-experiment power calculations
- Sample size recommendations
- Effect size estimation
- Bayesian alternative suggestions

### 9. Interactive Reports (Priority: LOW)
Generate interactive HTML reports:
- Expandable issue details
- Code diff visualization
- Trend analysis across commits
- Team-level dashboards

### 10. Community Rules Repository (Priority: LOW)
Create infrastructure for community-contributed rules:
```bash
scilint rules install domain-specific-rules/neuroscience
scilint rules publish my-custom-rules
```

---

## Technical Requirements

### Code Quality
- 100% type hints (mypy strict mode)
- >90% test coverage
- Documentation for all public APIs
- Performance: <5s for 10,000 LOC

### Backwards Compatibility
- All v1.0 CLI commands must work unchanged
- Config files are optional (sensible defaults)
- Graceful degradation when optional deps missing

### Security
- No code execution during analysis (AST only)
- Sandboxed execution for auto-fix preview
- Signed rule packages for community rules

---

## Implementation Order

### Sprint 1: Foundation (Launch-Critical)
1. Configuration system (`.scilintrc.yaml`)
2. Domain profiles (physics, biology, economics)
3. Pre-commit hook improvements
4. Bug fixes from KNOWN_ISSUES.md

### Sprint 2: Developer Experience
5. Auto-fix mode
6. VS Code extension (basic)
7. Jupyter magic commands

### Sprint 3: Advanced Analysis
8. Cross-file taint analysis
9. ReproducibilityGuard
10. TensorFlow/scikit-learn support

### Sprint 4: Community
11. Interactive HTML reports
12. Community rules repository
13. Team dashboards

---

## Success Metrics

1. **Adoption**: GitHub stars, PyPI downloads, CI integrations
2. **Coverage**: % of scientific code patterns detected
3. **False Positive Rate**: <5% for default profiles
4. **Fix Rate**: >80% of issues have auto-fix available
5. **Performance**: <1s latency for incremental checks

---

## Philosophy Reminders

1. **Educational First**: Every warning must explain WHY it matters scientifically
2. **Empowering, Not Blocking**: Help scientists find truth, don't just fail builds
3. **Domain Expertise**: Rules must be validated by domain experts
4. **Transparency**: Open-source, auditable, reproducible
5. **Minimal False Positives**: Better to miss issues than cry wolf

---

## Getting Started

```bash
# Clone and setup
git clone <repo>
cd scilint
pip install -e ".[dev]"

# Run existing tests
python -m pytest scilint/tests/ -v

# Start with configuration system
# See: scilint/config/ (to be created)
```

**Go forth and build the immune system for ALL of science.**
