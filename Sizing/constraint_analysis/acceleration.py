from Sizing.MissionProfile.Segments import Mission_segments
from Sizing.utils.atmosphere import Atmosphere
from Sizing.propulsion.assumptions import thrust_lapse, TSFC
import numpy as np
import Sizing.utils.Constants as const
import Sizing.utils.utils as utils
from Sizing.Variable_info.variables import Aircraft
import Sizing.aerodynamics.Assumptions


def acceleration(time, EAS_Start, EAS_End):
    "Compute the acceleration"
    return utils.knots_to_fts(EAS_End - EAS_Start) / (time * const.SL_GRAVITY_FT)


def Thrust_Weight_Ratio(
    wing_loading, mission_acceleration: Mission_segments.acceleration
):
    print("Acceleration")

    beta = mission_acceleration.weight_fraction.value
    altitude = mission_acceleration.altitude.value
    EAS_Start = mission_acceleration.KEAS_start.value
    EAS_End = mission_acceleration.KEAS_end.value
    time = mission_acceleration.time.value
    K1 = Aircraft.Aerodynamics.K1.value
    K2 = Aircraft.Aerodynamics.K2.value
    atm = Atmosphere(altitude)
    Mach_start = utils.KEAS_to_Mach(EAS_Start, altitude)
    Mach_end = utils.KEAS_to_Mach(EAS_End, altitude)
    q_start = (
        0.5 * Atmosphere(0).density_slug_ft3.value * utils.knots_to_fts(EAS_Start) ** 2
    )
    q_end = (
        0.5 * Atmosphere(0).density_slug_ft3.value * utils.knots_to_fts(EAS_End) ** 2
    )
    q = (q_start + q_end) / 2

    Cd0_start = Sizing.aerodynamics.Assumptions.Cd0(Mach_start, altitude)
    Cd0_end = Sizing.aerodynamics.Assumptions.Cd0(Mach_end, altitude)
    Cd0 = (Cd0_start + Cd0_end) / 2

    alpha_start = thrust_lapse(Mach_start, atm.density_ratio.value)
    alpha_end = thrust_lapse(Mach_end, atm.density_ratio.value)
    alpha = (alpha_start + alpha_end) / 2

    ### Debugging ###
    # print(Mach_start,Mach_end)
    # print(q_start,q_end)
    # print(Cd0_start,Cd0_end)
    # print(alpha_start,alpha_end)
    linear_term = K1 * (beta / q) * wing_loading
    Inverse_term = Cd0 / ((beta / q) * wing_loading)
    T_W = (beta / alpha) * (
        linear_term + K2 + Inverse_term + acceleration(time, EAS_Start, EAS_End)
    )
    return T_W
