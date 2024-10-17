import numpy as np
from Sizing.utils.atmosphere import Atmosphere, SL_SOUND_SPEED


"""
This module provides various utility functions for unit conversions and calculations related 
to aircraft speeds and altitudes.
"""

SOUND_SPEED_AT_SEA_LEVEL = 340.29  # m/s


def knots_to_mps(knots):
    """
    Convert speed from knots to meters per second (m/s).
    Parameters:
    knots (float): Speed in knots.
    Returns:
    float: Speed in meters per second (m/s).
    """

    return knots * 1852 / 3600


def mps_to_knots(mps):
    """
    Convert speed from meters per second (mps) to knots.
    Parameters:
    mps (float): Speed in meters per second.
    Returns:
    float: Speed in knots.
    """

    return mps * 3600 / 1852


def nmi_to_ft(nmi):
    """
    Convert nautical miles to feet.
    Parameters:
    nmi (float): Nautical miles.
    Returns:
    float: Feet.
    """
    return nmi * 6076.1155


def KEAS_to_Mach(KEAS, altitude, meter=False):
    """
    This function calculates the Mach number of the aircraft based on the equivalent airspeed.
    use the definition of equivalent airspeed $$KEAS = a_0M \sqrt(P/P_0)$$
    Parameters:
        KEAS (float): Equivalent airspeed of the aircraft in knots.
        altitude (float): Altitude of the aircraft in feet
        meter(bool): True if altitude in meter, False if it is in feet
    Returns:
        float: Mach number.
    """
    atm = Atmosphere(altitude, meter)
    return (knots_to_mps(KEAS) / SL_SOUND_SPEED) / (np.sqrt(atm.pressure_ratio.value))


def Mach_to_KEAS(Mach, altitude, meter=False):
    """
    This function calculates the equivalent airspeed (KEAS) of the aircraft based on the Mach number.
    Parameters:
        Mach (float): Mach number of the aircraft.
        altitude (float): Altitude of the aircraft in feet.
        meter (bool): True if altitude is in meters, False if it is in feet.
    Returns:
        float: Equivalent airspeed in knots.
    """
    atm = Atmosphere(altitude, meter)
    KEAS = Mach * SL_SOUND_SPEED * np.sqrt(atm.pressure_ratio.value)
    return mps_to_knots(KEAS)


def KEAS_to_TAS(KEAS, altitude, meter=False):
    atm = Atmosphere(altitude, meter)
    return KEAS / np.sqrt(atm.density_ratio.value)


def TAS_to_KEAS(TAS, altitude, meter=False):
    atm = Atmosphere(altitude, meter)
    return TAS * np.sqrt(atm.density_ratio.value)


def Mach_to_TAS(Mach, altitude, meter=False):
    """
    This function calculates the true airspeed (TAS) of the aircraft based on the Mach number.
    Parameters:
        Mach (float): Mach number of the aircraft.
        altitude (float): Altitude of the aircraft in feet.
        meter (bool): True if altitude is in meters, False if it is in feet.
    Returns:
        float: True airspeed in knots.
    """
    EAS = Mach_to_KEAS(Mach, altitude, meter)
    TAS = KEAS_to_TAS(EAS, altitude, meter)
    return TAS


def TAS_to_Mach(TAS, altitude, meter=False):
    """
    This function calculates the Mach number of the aircraft based on the true airspeed.
    Parameters:
        TAS (float): True airspeed of the aircraft in knots.
        altitude (float): Altitude of the aircraft in feet.
        meter (bool): True if altitude is in meters, False if it is in feet.
    Returns:
        float: Mach number.
    """
    EAS = TAS_to_KEAS(TAS, altitude, meter)
    Mach = KEAS_to_Mach(EAS, altitude, meter)
    return Mach


def ft_to_meter(ft):
    """
    This function converts feet to meters.
    Returns:
        float: Meters.
    """
    return ft * 0.3048


def meter_to_ft(meter):
    """
    This function converts meters to feet.
    Returns:
        float: Feet.
    """
    return meter / 0.3048


def knots_to_fts(knots):
    """
    Convert speed from knots to feet per second (ft/s).
    Parameters:
    knots (float): Speed in knots.
    Returns:
    float: Speed in feet per second (ft/s).
    """
    return knots * 1.68781


def fts_to_knots(fts):
    """
    Convert speed from feet per second (fts) to knots.
    Parameters:
    fts (float): Speed in feet per second.
    Returns:
    float: Speed in knots.
    """
    return fts / 1.68781


def crossover_altitude(Mach_goal, Speed_EAS, accuracy=100):
    """
    Calculate the crossover altitude where a given equivalent airspeed (EAS)
    reaches a specified Mach number.
    Args:
        Mach_goal (float): The target Mach number to reach.
        Speed_EAS (float): The equivalent airspeed (EAS) in knots.
    Returns:
        int: The altitude in feet at which the specified Mach number is reached.
    """

    alt = 20000  # Initial altitude in feet, since the goal mach will ve reached at a higher altitude, we can start from a high altitude
    step = accuracy  # Step size in feet , accuarcy of the calculation
    while True:
        Mach = KEAS_to_Mach(Speed_EAS, alt)
        if Mach >= Mach_goal:
            break
        alt += step
    return alt
