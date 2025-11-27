def calculate_trajectory(time_seconds, initial_velocity_mps):
    """
    Calculate particle trajectory.
    Contains dimensional analysis errors that Demyst detects.
    """
    g = 9.81  # Acceleration [L T^-2]
    
    # Correct: Distance = Velocity * Time
    distance_x = initial_velocity_mps * time_seconds
    
    # ERROR: Adding scalar to dimensioned quantity
    # "The fudge factor"
    distance_y = 0.5 * g * (time_seconds ** 2) + 5.0
    
    # ERROR: Adding Time to Distance
    # "Relativistic correction" (physically nonsense)
    total_metric = distance_x + time_seconds
    
    return total_metric

def verify_energy(mass_kg, velocity_mps):
    # ERROR: Assigning Energy [M L^2 T^-2] to Force [M L T^-2] variable
    force_impact = 0.5 * mass_kg * (velocity_mps ** 2)
    return force_impact
