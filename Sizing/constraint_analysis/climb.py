from Sizing.Variable_info.Variable import Variable
import Sizing.aerodynamics
import Sizing.aerodynamics.Assumptions

"""
Calculate the thrust to weight ratio for climb with the given constraints 
"""
from Sizing.MissionProfile.Segments import Mission_segments
from Sizing.utils.atmosphere import Atmosphere
from Sizing.propulsion.assumptions import thrust_lapse, TSFC
import numpy as np
import Sizing.utils.Constants as const
import Sizing.utils.utils as utils
from Sizing.Variable_info.variables import Aircraft
import Sizing


def Thrust_to_weight_ratio(
    wing_loading, beta, ROC, speed_EAS=None, start_alt=0, end_alt=10000, Mach=None
):
    """
    Calculate the thrust-to-weight ratio for climb.
    2 cases are considered:
    1. Climb at constant Mach number
    2. Climb at constant equivalent airspeed (EAS)
    Args:
        wing_loading (float): Wing loading in lb/ft^2.
        beta (float): Weight fraction (beta) at the end of the phase.
        ROC (float): Rate of climb in ft/min.
        speed_EAS (float): Equivalent airspeed in knots.
        start_alt (float): Start altitude in feet.
        end_alt (float): End altitude in feet.
        Mach (float): Mach number.
    Returns:
    float: Thrust-to-weight ratio required for climb.
    """
    ROC = ROC / 60  # Convert ROC from ft/min to ft/s
    sigma_start = Atmosphere(start_alt).density_ratio.value
    sigma_end = Atmosphere(end_alt).density_ratio.value
    sigma = (sigma_start + sigma_end) / 2
    K1 = Aircraft.Aerodynamics.K1.value
    K2 = Aircraft.Aerodynamics.K2.value
    if Mach:
        if ROC > 0:
            print("climbing at constant Mach")
        else:
            print("Descending at constant Mach")
        ### Climb at constant Mach number
        q_start = (
            0.5
            * Atmosphere(0).density_slug_ft3.value
            * utils.knots_to_fts(utils.Mach_to_KEAS(Mach, start_alt)) ** 2
        )
        q_end = (
            0.5
            * Atmosphere(0).density_slug_ft3.value
            * utils.knots_to_fts(utils.Mach_to_KEAS(Mach, end_alt)) ** 2
        )
        q = (q_start + q_end) / 2
        Cd0_start = Sizing.aerodynamics.Assumptions.Cd0(Mach, start_alt)
        Cd0_end = Sizing.aerodynamics.Assumptions.Cd0(Mach, end_alt)
        Cd0 = (Cd0_start + Cd0_end) / 2
        V_start = utils.Mach_to_TAS(Mach, start_alt)
        V_end = utils.Mach_to_TAS(Mach, end_alt)
        V = (V_start + V_end) / 2
        alpha = thrust_lapse(Mach, sigma)
    if speed_EAS:
        if ROC > 0:
            print("climbing at constant EAS")
        else:
            print("Descending at constant EAS")
        ### Climb at constant EAS speed
        q = (
            0.5
            * Atmosphere(0).density_slug_ft3.value
            * utils.knots_to_fts(speed_EAS) ** 2
        )
        Cd0_start = Sizing.aerodynamics.Assumptions.Cd0(
            utils.KEAS_to_Mach(speed_EAS, start_alt), start_alt
        )
        Cd0_end = Sizing.aerodynamics.Assumptions.Cd0(
            utils.KEAS_to_Mach(speed_EAS, end_alt), end_alt
        )
        V_start = utils.KEAS_to_TAS(speed_EAS, start_alt)  ### TAS  is in knots
        V_end = utils.KEAS_to_TAS(speed_EAS, end_alt)
        Cd0 = (Cd0_start + Cd0_end) / 2
        V = utils.knots_to_fts((V_start + V_end) / 2)

        alpha_star = thrust_lapse(utils.KEAS_to_Mach(speed_EAS, start_alt), sigma_start)
        alpha_end = thrust_lapse(utils.KEAS_to_Mach(speed_EAS, end_alt), sigma_end)
        alpha = (alpha_star + alpha_end) / 2

    linear_term = K1 * (beta / q) * wing_loading
    Inverse_ter = Cd0 / ((beta / q) * wing_loading)
    T_W = (beta / alpha) * (linear_term + K2 + Inverse_ter + ROC / V)
    return T_W


def Thrust_to_weight_ratio_2(wing_loading, mission_segment: Mission_segments.climb):
    return Thrust_to_weight_ratio(
        wing_loading,
        beta=mission_segment.weight_fraction.value,
        ROC=mission_segment.climb_rate.value,
        speed_EAS=mission_segment.KEAS.value,
        start_alt=mission_segment.start_altitude.value,
        end_alt=mission_segment.end_altitude.value,
        Mach=mission_segment.MACH.value,
    )


def crossover_altitude(Mach_goal, Speed_EAS):
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
    step = 100  # Step size in feet , accuarcy of the calculation
    while True:
        Mach = utils.KEAS_to_Mach(Speed_EAS, alt)
        if Mach >= Mach_goal:
            break
        alt += step
    return alt
