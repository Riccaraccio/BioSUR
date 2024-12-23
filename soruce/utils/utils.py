import numpy as np


# Unused for now
def check_composition(values: np.ndarray) -> bool:
    """Check if the composition values are valid"""
    if not np.isclose(np.sum(values), 1.0):
        return False
    if not all(0 <= value <= 1 for value in values):
        return False
    return True