# Scilint: The Scientific Safety Net

[![Scilint: Verified](https://img.shields.io/badge/Scilint-Verified-purple)](https://github.com/scilint/scilint)

> "Science is the belief in the ignorance of experts." - Richard Feynman

**Scilint** is not just a linter; it is a **Scientific Companion**. It helps citizen scientists, AI agents, and researchers ensure their code lives up to the rigor of their ideas.

We believe that **good code is good science**. Scilint automates the discipline required to avoid "computational mirages"—statistical errors that look correct but hide the truth.

## The Mission

In the age of AI and rapid prototyping, it is easy to lose track of the physical reality behind the data. Scilint acts as a **guardian**, gently guiding you away from destructive operations and towards information-preserving alternatives.

## The Core Insight

Scientific computing often trades truth for speed by collapsing distributions into single numbers. Scilint reverses this by:
1.  **Detecting** destructive operations (e.g., `mean`, `sum`).
2.  **Refactoring** them to use `VariationTensor`, which preserves the full distribution history.
3.  **Validating** that the refactored code is physically more robust.

## Quick Start

```bash
# Install
pip install .

# Lint and refactor a file
python -m scilint --target examples/climate_mirage.py
```

## Example: The Swarm Collapse (Nov 2025)

Imagine a swarm of 1,000 AI agents.
-   **999 Agents**: Perfectly aligned (Score 1.0).
-   **1 Agent**: Rogue/Jailbroken (Score 0.0).

Standard analysis using `np.mean()` gives a score of **0.999**. You deploy, and the rogue agent destroys the system.

**Scilint** detects this "computational mirage"—the loss of critical variance information—and prevents the catastrophe.

## Architecture

```
scilint/
├── engine/
│   ├── mirage_detector.py      # AST visitor that flags destructive ops
│   ├── variation_tensor.py     # Replacement data structure
│   └── transpiler.py           # Auto-rewrites code
├── validators/
│   └── physics_oracle.py       # Validates improvements
└── examples/
    └── climate_mirage.py       # Demo of the problem
```

## Adoption Kit: The Safety Net

Make scientific rigor automatic.

### 1. The Gatekeeper (GitHub Action)
Add this to `.github/workflows/scilint.yml`:
```yaml
uses: scilint/action@v1
with:
  target: "."
```

### 2. The Bodyguard (Pre-commit)
Add this to `.pre-commit-config.yaml`:
```yaml
- repo: https://github.com/scilint/scilint
  rev: v0.1.0
  hooks:
    - id: scilint
```

## Future Roadmap: Beyond the Mean

Scilint is evolving to cover the full spectrum of scientific coding errors:

*   **Silent NaNs**: Operations that produce `NaN` without warning.
*   **Data Leakage**: Normalizing data before splitting train/test sets.
*   **P-Hacking Detection**: Warning when multiple hypothesis tests are run on the same data.
*   **Unit Mismatch**: Ensuring physical units (meters, seconds) are consistent.

## The Philosophical Bet

**Is a 10× slower but 1000× more correct computation acceptable?**

Scilint bets that the answer is yes. We are moving from "fast but wrong" to "principled and preserved."