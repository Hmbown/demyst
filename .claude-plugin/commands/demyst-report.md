---
description: Generate a detailed scientific integrity report for documentation or PRs
arguments:
  - name: path
    description: File or directory to analyze
    required: false
  - name: format
    description: Output format (markdown or json)
    required: false
---

Generate a comprehensive scientific integrity report.

## Instructions

1. If path not provided, use current file or cwd.

2. Run comprehensive analysis and generate report:
   ```bash
   demyst report <path> --format markdown
   ```

3. The report includes:
   - **Summary**: Overall status (PASS/WARNING/FAIL)
   - **Mirages**: Variance-destroying operations
   - **Leakage**: Data contamination issues
   - **Hypothesis**: Statistical validity
   - **Tensor**: Deep learning integrity
   - **Units**: Dimensional analysis

4. For each section:
   - Status badge (PASS/FAIL/WARNING)
   - Issues found with line numbers
   - Scientific impact explanation
   - Actionable recommendations

5. Format options:
   - `markdown` (default): Good for PRs, documentation
   - `json`: Good for programmatic use

6. If the user wants a certificate:
   ```bash
   demyst report <path> --cert
   ```
   This generates a cryptographic proof of verification.

## Use Cases

- Add to PR descriptions for code review
- Include in paper methodology sections
- Document compliance for reproducibility
- Generate CI/CD quality gates
