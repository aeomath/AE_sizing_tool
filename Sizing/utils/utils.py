import ussa1976 as ussa
import numpy as np
from Sizing.utils.atmosphere import Atmosphere, SL_SOUND_SPEED

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
