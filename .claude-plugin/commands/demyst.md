---
description: Run comprehensive demyst scientific integrity analysis on a file or directory
arguments:
  - name: path
    description: File or directory to analyze (defaults to current file or cwd)
    required: false
---

Run comprehensive Demyst scientific integrity analysis.

## Instructions

1. If a path is provided, use it. Otherwise:
   - If in a Python file context, analyze that file
   - Otherwise, analyze the current working directory

2. Run the analysis using the CLI:
   ```bash
   demyst analyze <path> --format markdown
   ```

3. Report results organized by guard:
   - **Mirages** (CRITICAL): Variance-destroying operations
   - **Leakage** (CRITICAL): Train/test data contamination
   - **Hypothesis** (WARNING): Statistical validity issues
   - **Tensor** (WARNING): Deep learning integrity
   - **Units** (WARNING): Dimensional consistency

4. For each issue found, show:
   - Line number
   - Severity (CRITICAL/WARNING)
   - Brief description
   - Recommended fix

5. If CRITICAL issues are found, offer to run `/demyst-fix` to auto-fix mirages.

6. Summarize with overall status: PASS / WARNING / FAIL
