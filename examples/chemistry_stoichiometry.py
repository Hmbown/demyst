def calculate_molarity(mass_g, molar_mass_g_mol, volume_l):
    """
    Calculate solution molarity.
    Contains stoichiometry errors that Scilint detects.
    """
    # Correct: Moles = Mass / Molar Mass
    moles = mass_g / molar_mass_g_mol
    
    # ERROR: Adding Mass to Moles
    # "Total substance" (physically nonsense)
    total_substance = mass_g + moles
    
    # ERROR: Assigning Mass [M] to Concentration [N L^-3] variable
    concentration_result = mass_g * 2
    
    return concentration_result

def check_reaction_balance(reactants_moles, products_moles):
    # ERROR: Comparing Moles [N] to Mass [M] (implied by variable name)
    mass_limit = 100.0
    
    if reactants_moles > mass_limit:
        print("Reaction too large")
