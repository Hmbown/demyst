---
description: Auto-fix demyst violations (mirages) in a Python file
arguments:
  - name: path
    description: File to fix (defaults to current file)
    required: false
  - name: dry-run
    description: Preview changes without applying (default true)
    required: false
---

Auto-fix scientific integrity violations in Python code.

## Instructions

1. If path not provided, use the current file context.

2. First, run analysis to detect issues:
   ```bash
   demyst analyze <path> --format json
   ```

3. Show which issues are auto-fixable:
   - **Mirage violations** (mean, sum, argmax, argmin) - CAN be auto-fixed
   - Other violations - require manual fixes

4. If `dry-run` is true or not specified, preview changes:
   ```bash
   demyst mirage <path> --fix --dry-run
   ```
   Show the diff of proposed changes.

5. Ask user to confirm before applying fixes.

6. If user confirms and dry-run is false:
   ```bash
   demyst mirage <path> --fix
   ```

7. Re-run analysis to verify fixes were applied correctly.

8. Report remaining issues that need manual attention.

## Notes

- Only mirage violations can be auto-fixed (transforms to VariationTensor)
- Leakage issues require manual restructuring of code
- Statistical issues require manual correction selection
