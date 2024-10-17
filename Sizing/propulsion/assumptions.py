import numpy as np
from Sizing.Variable_info.variables import Aircraft

"""
This module contains functions related to propulsion assumptions for aircraft sizing.
See section IV.A of the report for more details.
Functions:
    thrust_lapse(Mach_inf, density_ratio):
        Calculates the thrust lapse of the engine, which is used to determine the thrust required at different altitudes.
    TSFC(Mach_inf, Temp_ratio):
        Calculates the thrust specific fuel consumption (TSFC) of the engine, which is used to determine the fuel consumption at different altitudes.
"""


def thrust_lapse(Mach_inf, density_ratio):
    """
    This function calculates the thrust lapse of the engine.
    It is used to calculate the thrust required at different altitudes.
    The thrust lapse is calculated as:

    Returns:
        float: Thrust lapse.
    """
    temp1 = (1.2 - Mach_inf) ** 3
    return (0.568 + 0.25 * (temp1)) * density_ratio**0.6


def TSFC(Mach_inf, Temp_ratio):
    """
    This function calculates the thrust specific fuel consumption (TSFC) of the engine.
    It is used to calculate the thrust required at different altitudes.
    The TSFC is calculated as:

    Returns:
        float: Thrust specific fuel consumption.
    """
    return (
        np.sqrt(Temp_ratio) * Aircraft.Propulsion.ktsfc.value * (0.45 + 0.54 * Mach_inf)
    ) / 3600  ## convert from 1/hr to 1/s
