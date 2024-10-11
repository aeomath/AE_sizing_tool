import numpy as np
from Sizing.Variable_info.variables import Aircraft

### Constants
K1 = 0.0556
K2 = -0.0197


def Cd0(Mach_inf, altitude):
    """
    This function calculates the zero-lift drag coefficient of the aircraft.
    It is used to calculate the drag of the aircraft.

    Returns:
        float: Zero-lift drag coefficient.
    """
    temp1 = (1 / (np.sqrt(1 - Mach_inf**2)) - 1.273) ** 2
    temp2 = 0.0027 / (np.sqrt(1 - Mach_inf**2))
    return 0.0311 * temp1 - temp2 + 7.86e-8 * altitude + 0.0215


def Cdi(Cl):
    """
    This function calculates the induced drag coefficient of the aircraft.
    Returns:
        float: Drag coefficient.
    """
    return Aircraft.Aerodynamics.K1.value * Cl**2 + Aircraft.Aerodynamics.K2.value * Cl
