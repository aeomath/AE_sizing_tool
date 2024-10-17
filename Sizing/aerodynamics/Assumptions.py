import numpy as np

from Sizing.Variable_info.variables import Aircraft


K1 = Aircraft.Aerodynamics.K1.value
K2 = Aircraft.Aerodynamics.K2.value

"""
This module contains functions to calculate the aerodynamic drag coefficients of an aircraft.
See section IV.B of the report for more details.
Functions:
    Cd0(Mach_inf, altitude):
        Calculates the zero-lift drag coefficient of the aircraft.
    Cdi(Cl):
        Calculates the induced drag coefficient of the aircraft.
"""


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
    return K1 * Cl**2 + K2 * Cl
