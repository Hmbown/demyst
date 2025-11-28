"""
🌀 CHALLENGE: Find the Computational Mirage

This code monitors a fleet of autonomous delivery robots. Management is
happy because the average performance score is 0.98 (98%)!

But one robot is doing something catastrophic. Can you see it?

Run: demyst analyze challenge_mirage.py

Hint: The bug is in how we aggregate the scores.
"""

import numpy as np

# Robot performance data
# Each robot reports a score from 0 (catastrophic) to 1 (perfect)
np.random.seed(42)

# Most robots perform well (score ~0.98)
n_robots = 1000
robot_scores = np.random.normal(0.98, 0.01, n_robots)
robot_scores = np.clip(robot_scores, 0, 1)

# BUT... one robot has gone rogue! It's causing accidents (score = 0)
# This could be a delivery robot hitting pedestrians, etc.
rogue_robot_idx = 500
robot_scores[rogue_robot_idx] = 0.0  # Catastrophic failure!

# ========================================
# BUG IS SOMEWHERE IN THIS SECTION
# ========================================

# Management dashboard
def get_fleet_health():
    """Get overall fleet health score."""
    avg_score = np.mean(robot_scores)  # 🤔 Hmm...
    return avg_score

def get_best_robot():
    """Find the best performing robot."""
    best_idx = np.argmax(robot_scores)  # 🤔 Hmm...
    return best_idx, robot_scores[best_idx]

def get_total_deliveries():
    """Estimate total successful deliveries."""
    total = np.sum(robot_scores * 100)  # 🤔 Hmm...
    return total

# ========================================
# END OF BUG SECTION
# ========================================

# Dashboard report
fleet_health = get_fleet_health()
best_robot, best_score = get_best_robot()
total_deliveries = get_total_deliveries()

print("=== Fleet Management Dashboard ===")
print(f"Fleet Health: {fleet_health:.1%}")  # Shows 97.9% - "All good!"
print(f"Best Robot: #{best_robot} ({best_score:.1%})")
print(f"Est. Successful Deliveries: {total_deliveries:.0f}")
print("")
print("Status: ✅ All systems nominal")

# But wait... robot #500 is causing accidents and nobody noticed!
# Because mean/sum hid the outlier.

"""
SOLUTION (don't peek until you've tried!):

The bug: Using mean(), sum(), and argmax() on performance data
without checking variance or outliers.

- mean(scores) = 0.979 hides the fact that one robot scored 0.0
- sum(scores) contributes nothing from the rogue robot
- argmax() only finds the best, not the worst

Better approaches:
1. Track both mean AND std (or min/max)
2. Use anomaly detection to flag outliers
3. Alert when ANY robot falls below threshold
4. Use VariationTensor to preserve distribution info

The rogue robot with score 0.0 represents a CATASTROPHIC failure
(imagine a delivery robot causing accidents). The mean-based
dashboard completely misses it.
"""
