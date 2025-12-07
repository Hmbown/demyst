"""
Real-World Computational Mirages

These examples demonstrate how np.mean() and similar aggregations
can hide critical information in real scientific contexts.

Run: demyst mirage examples/real_world_mirages.py
"""

import numpy as np

# =============================================================================
# 1. ANSCOMBE'S QUARTET - Same Mean, Wildly Different Distributions
# =============================================================================
# Four datasets with identical means (~7.5) but completely different patterns.
# Aggregating destroys the ability to distinguish linear, quadratic, outlier,
# and leverage-point relationships.


def anscombe_mirage():
    """All four datasets have mean_y = 7.5, but they're fundamentally different."""
    # Dataset I: Linear relationship
    y1 = np.array([8.04, 6.95, 7.58, 8.81, 8.33, 9.96, 7.24, 4.26, 10.84, 4.82, 5.68])

    # Dataset II: Quadratic relationship (not linear at all!)
    y2 = np.array([9.14, 8.14, 8.74, 8.77, 9.26, 8.10, 6.13, 3.10, 9.13, 7.26, 4.74])

    # Dataset III: Perfect linear except one outlier at (13, 12.74)
    y3 = np.array([7.46, 6.77, 12.74, 7.11, 7.81, 8.84, 6.08, 5.39, 8.15, 6.42, 5.73])

    # Dataset IV: All points at x=8 except one leverage point
    y4 = np.array([6.58, 5.76, 7.71, 8.84, 8.47, 7.04, 5.25, 12.50, 5.56, 7.91, 6.89])

    # THE MIRAGE: All means are ~7.5, hiding completely different structures
    mean1 = np.mean(y1)  # 7.50
    mean2 = np.mean(y2)  # 7.50 - but this is a parabola!
    mean3 = np.mean(y3)  # 7.50 - but there's an outlier at 12.74!
    mean4 = np.mean(y4)  # 7.50 - but there's a leverage point!

    return mean1, mean2, mean3, mean4


# =============================================================================
# 2. SIMPSON'S PARADOX - UC Berkeley Admissions (1973)
# =============================================================================
# Aggregated data showed 44% male vs 35% female admission rate.
# But when stratified by department, women were MORE likely to be admitted
# in 4 out of 6 departments. Women applied to more competitive departments.


def simpsons_paradox_mirage():
    """Aggregated admission rates hide department-level truth."""
    # Simplified version of the Berkeley data
    # Department A (easy): 62% admit rate, mostly male applicants
    dept_a_admits = np.array([1] * 512 + [0] * 313)  # 62% admitted

    # Department F (hard): 6% admit rate, mostly female applicants
    dept_f_admits = np.array([1] * 22 + [0] * 351)  # 6% admitted

    # THE MIRAGE: Overall mean hides that success depends on department choice
    overall_rate = np.mean(np.concatenate([dept_a_admits, dept_f_admits]))

    # A researcher seeing only overall_rate would miss the confounding variable
    return overall_rate


# =============================================================================
# 3. FAT TAILS - Stock Market Returns
# =============================================================================
# Average daily returns look benign (~0.04%), but this hides
# Black Monday (-22.6%), 2008 crash, 2020 crash, etc.
# Normal distribution would predict these are 25-sigma events (impossible).


def fat_tails_mirage():
    """Average return hides catastrophic tail events."""
    np.random.seed(42)

    # 10 years of "normal" daily returns (~252 trading days/year)
    normal_days = np.random.normal(0.0004, 0.01, 2500)  # ~0.04% mean, 1% std

    # But reality has fat tails - these actually happened:
    black_monday_1987 = -0.226  # -22.6% in ONE DAY
    flash_crash_2010 = -0.0656  # -6.56% intraday
    covid_crash_2020 = -0.1198  # -11.98% single day

    all_returns = np.concatenate(
        [normal_days, [black_monday_1987, flash_crash_2010, covid_crash_2020]]
    )

    # THE MIRAGE: Mean looks fine, variance looks reasonable
    avg_return = np.mean(all_returns)  # ~0.03% - seems safe!
    volatility = np.std(all_returns)  # Underestimates true risk

    # But the 0.03% average hid the -22.6% Black Monday
    # Using mean for risk assessment would be catastrophically wrong

    return avg_return, volatility


# =============================================================================
# 4. OUTLIER MASKING - Multiple Outliers Hide Each Other
# =============================================================================
# When you have multiple outliers, they pull the mean toward them,
# making standard outlier tests (Grubbs, Z-score) fail to detect ANY of them.


def outlier_masking_mirage():
    """Two outliers mask each other by distorting mean and std."""
    # Normal measurements
    normal_data = np.array([10.2, 10.5, 9.8, 10.1, 10.3, 9.9, 10.0, 10.4])

    # Two equipment malfunctions produced extreme values
    outliers = np.array([25.0, 28.0])  # Should be obvious outliers

    all_data = np.concatenate([normal_data, outliers])

    # THE MIRAGE: Mean is pulled toward outliers
    mean_val = np.mean(all_data)  # ~12.4 instead of ~10.15
    std_val = np.std(all_data)  # Inflated by outliers

    # Z-score test now FAILS to detect the outliers because
    # the mean and std are already corrupted by them
    z_scores = (all_data - mean_val) / std_val
    # The 25.0 and 28.0 values won't exceed z=3 threshold!

    return mean_val, std_val, z_scores


# =============================================================================
# 5. CLIMATE EXTREMES - Average Temperature Hides Heatwaves
# =============================================================================
# Mean annual temperature might only rise 2C, but this hides
# dramatic increases in extreme heat days that kill people.


def climate_extremes_mirage():
    """Average temperature hides deadly extreme events."""
    np.random.seed(123)

    # Historical temperature distribution (baseline)
    baseline_temps = np.random.normal(20, 5, 365)  # mean 20C, std 5C

    # Climate change: mean shifts slightly, but extremes shift MORE
    # (variance increases, not just mean)
    future_temps = np.random.normal(22, 7, 365)  # mean 22C, std 7C

    # THE MIRAGE: Mean only increased 2C
    baseline_mean = np.mean(baseline_temps)  # ~20C
    future_mean = np.mean(future_temps)  # ~22C  (only +2C, seems mild)

    # But extreme heat days (>35C) increased dramatically
    baseline_extreme_days = np.sum(baseline_temps > 35)  # ~1-2 days
    future_extreme_days = np.sum(future_temps > 35)  # ~10-15 days

    # The +2C average hides a 5-10x increase in deadly heat days
    return baseline_mean, future_mean


# =============================================================================
# 6. SWARM SAFETY - One Rogue Agent Hidden by 999 Good Ones
# =============================================================================
# (From demyst's original example)


def swarm_safety_mirage():
    """Mean alignment score hides the one rogue agent that causes cascade failure."""
    agent_count = 1000

    # 999 agents are perfectly aligned (score = 1.0)
    # 1 agent is compromised/rogue (score = 0.0)
    alignment_scores = np.ones(agent_count)
    alignment_scores[-1] = 0.0  # Rogue agent

    # THE MIRAGE: Average looks great!
    mean_alignment = np.mean(alignment_scores)  # 0.999 - seems safe!

    # Decision based on mean: "Deploy! Average alignment > 0.99"
    # Reality: The one rogue agent initiates cascade failure

    return mean_alignment


# =============================================================================
# MAIN - Run all examples
# =============================================================================

if __name__ == "__main__":
    print("=== Anscombe's Quartet ===")
    m1, m2, m3, m4 = anscombe_mirage()
    print(f"All means: {m1:.2f}, {m2:.2f}, {m3:.2f}, {m4:.2f} (identical!)")
    print("But datasets are: linear, quadratic, outlier, leverage point\n")

    print("=== Simpson's Paradox ===")
    rate = simpsons_paradox_mirage()
    print(f"Overall admission rate: {rate:.1%}")
    print("Hides that women were MORE likely admitted per-department\n")

    print("=== Fat Tails (Stock Returns) ===")
    avg, vol = fat_tails_mirage()
    print(f"Average daily return: {avg:.4%}, Volatility: {vol:.4%}")
    print("Hides -22.6% Black Monday crash\n")

    print("=== Outlier Masking ===")
    mean_val, std_val, z = outlier_masking_mirage()
    print(f"Mean: {mean_val:.1f}, Std: {std_val:.1f}")
    print(f"Max Z-score: {max(abs(z)):.2f} (< 3, so outliers NOT detected!)\n")

    print("=== Climate Extremes ===")
    base, future = climate_extremes_mirage()
    print(f"Baseline: {base:.1f}C, Future: {future:.1f}C (+2C average)")
    print("But extreme heat days increased 5-10x\n")

    print("=== Swarm Safety ===")
    alignment = swarm_safety_mirage()
    print(f"Mean alignment: {alignment:.3f}")
    print("Hides the ONE rogue agent that causes cascade failure")
