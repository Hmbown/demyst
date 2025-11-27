# Demyst Launch Checklist 🚀

Ready for Hacker News!

## ✅ Completed Technical Tasks

- [x] **Type Safety**: Fixed all mypy errors in main package.
- [x] **CLI Polish**: Refactored CLI to use `rich` for beautiful, "hacker-friendly" output.
- [x] **Installation**: Verified `pip install -e .` in a fresh environment.
- [x] **Auto-Fix Logic**: Fixed CST transformer to correctly handle `np.mean(x)` vs `x.mean()`.
- [x] **Documentation**: Updated README to highlight AST parsing (addressing skepticism).
- [x] **Metadata**: Synced `setup.py` with `pyproject.toml`.

## 📝 To-Do Before Posting

1.  **PyPI Release**:
    ```bash
    python3 -m build
    python3 -m twine upload dist/*
    ```
2.  **Demo Asset**:
    - Record a 30s GIF of `demyst analyze examples/swarm_collapse.py` showing the beautiful output.
    - Add it to the top of `README.md`.
3.  **Colab Notebook**:
    - Create a "Try it now" Google Colab notebook.
    - Link it in the README.
4.  **Social Proof**:
    - Ensure the repository has a few initial stars/forks before posting to avoid the "empty repo" look.
5.  **The "First Comment"**:
    - Draft your first comment on HN explaining *why* you built this (the "Swarm Collapse" story is great).

## 🔍 Verified Commands

```bash
# Analyze a single file (Beautiful Output)
demyst analyze examples/swarm_collapse.py

# Analyze a directory
demyst analyze examples/

# Auto-fix a file (Dry Run)
demyst mirage examples/swarm_collapse.py --fix --dry-run
```
