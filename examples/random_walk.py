import numpy as np


def analyze_random_walk(steps=1000):
    """
    Analyze a random walk and calculate statistics.
    This function contains 'computational mirages' that PIPRE should detect.
    """
    # Generate random walk
    walk = np.cumsum(np.random.normal(0, 1, steps))

    # Destructive operations
    mean_pos = np.mean(walk)
    max_pos = np.max(walk)
    final_pos = walk[-1]

    # Premature discretization
    discrete_mean = int(mean_pos)

    return mean_pos, max_pos, discrete_mean


if __name__ == "__main__":
    mean_val, max_val, discrete = analyze_random_walk()
    print(f"Mean: {mean_val}")
    print(f"Max: {max_val}")
    print(f"Discrete Mean: {discrete}")
