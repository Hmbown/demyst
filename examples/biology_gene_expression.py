import numpy as np
from scipy.stats import ttest_ind


def analyze_gene_expression(num_genes=1000):
    """
    Analyze differential gene expression.
    Contains p-hacking patterns that Demyst detects.
    """
    print(f"Analyzing {num_genes} genes...")

    significant_genes = []

    # Simulate gene expression data
    # Null hypothesis: No difference between control and treatment
    control_group = np.random.normal(10, 2, (num_genes, 10))
    treatment_group = np.random.normal(10, 2, (num_genes, 10))

    # ERROR: Multiple comparisons without correction
    for gene_idx in range(num_genes):
        # Run t-test for each gene
        t_stat, p_val = ttest_ind(control_group[gene_idx], treatment_group[gene_idx])

        # ERROR: Conditional reporting / P-hacking
        if p_val < 0.05:
            print(f"Gene_{gene_idx} is SIGNIFICANT! (p={p_val:.4f})")
            significant_genes.append(gene_idx)

    return significant_genes
