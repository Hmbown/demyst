"""
📊 CHALLENGE: Find the P-Hacking

This code analyzes clinical trial data for a new drug. The researcher
finds a "significant" result and publishes! But the statistics are wrong.

Can you spot the p-hacking before running demyst?

Run: demyst analyze challenge_phacking.py

Hint: The bug is in how statistical tests are used.
"""

import numpy as np
from scipy import stats

np.random.seed(42)

# Clinical trial: Testing if a drug affects ANY biomarker
# (The drug actually does nothing - it's a placebo!)
n_patients = 100
n_biomarkers = 20  # Testing 20 different biomarkers

# Generate random data (drug has no effect)
control_group = np.random.randn(n_patients, n_biomarkers)
treatment_group = np.random.randn(n_patients, n_biomarkers)

# ========================================
# BUG IS SOMEWHERE IN THIS SECTION
# ========================================

print("Clinical Trial Results: Drug XYZ")
print("=" * 40)

significant_findings = []

# Test each biomarker
for i in range(n_biomarkers):
    control = control_group[:, i]
    treatment = treatment_group[:, i]

    # Perform t-test
    t_stat, p_value = stats.ttest_ind(control, treatment)

    # Check significance
    if p_value < 0.05:  # 🤔 Hmm...
        significant_findings.append(
            {"biomarker": f"Biomarker_{i}", "p_value": p_value, "t_stat": t_stat}
        )
        print(f"✓ Biomarker_{i}: p={p_value:.4f} - SIGNIFICANT!")

# ========================================
# END OF BUG SECTION
# ========================================

print("")
if significant_findings:
    print(f"CONCLUSION: Drug XYZ significantly affects {len(significant_findings)} biomarker(s)!")
    print("Recommendation: Proceed to Phase 3 trials")
else:
    print("CONCLUSION: No significant effects found")

# The drug does NOTHING, but we "found" significant results!

"""
SOLUTION (don't peek until you've tried!):

The bug: Testing 20 biomarkers without correcting for multiple comparisons.

With 20 tests at α=0.05, the expected number of false positives is:
20 × 0.05 = 1 false positive (even with random data!)

This is p-hacking / the multiple comparisons problem:
- Run many tests
- Report only the "significant" ones
- Publish and claim discovery

Correct approaches:
1. Bonferroni correction: α_corrected = 0.05 / 20 = 0.0025
2. Benjamini-Hochberg FDR correction
3. Pre-register which biomarker(s) you're testing

With Bonferroni correction (p < 0.0025), likely NO biomarkers
would be significant - revealing the drug has no effect.

This is a real problem in science: HARKing (Hypothesizing After
Results are Known) and selective reporting lead to non-replicable
findings.
"""
