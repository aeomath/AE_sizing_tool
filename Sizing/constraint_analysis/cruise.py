from Sizing.MissionProfile.Segments import Mission_segments
from Sizing.utils.atmosphere import Atmosphere
from Sizing.propulsion.assumptions import thrust_lapse, TSFC
import numpy as np
import Sizing.utils.Constants as const
import Sizing.utils.utils as utils
from Sizing.Variable_info.variables import Aircraft
import Sizing.aerodynamics.Assumptions


def Thrust_weight_ratio(
    wing_loading,
    mission_segment: Mission_segments.cruise,
    Equi_Speed=None,
    bank_angle=0,
):
    # print("Cruising segment")
    load_factor = 1 / np.cos(bank_angle * np.pi / 180)
    beta = mission_segment.weight_fraction.value
    altitude = mission_segment.altitude.value
    if Equi_Speed is not None:
        EAS = Equi_Speed
    else:
        EAS = mission_segment.EAS.value
    Mach = mission_segment.Mach.value

    alpha = thrust_lapse(Mach, Atmosphere(altitude).density_ratio.value)
    q = 0.5 * Atmosphere(0).density_slug_ft3.value * utils.knots_to_fts(EAS) ** 2
    Cd0 = Sizing.aerodynamics.Assumptions.Cd0(Mach, altitude)
    K1 = Aircraft.Aerodynamics.K1.value
    K2 = Aircraft.Aerodynamics.K2.value
    linear_term = K1 * (beta / q) * wing_loading
    Inverse_ter = Cd0 / ((beta / q) * wing_loading)
    T_W = (beta / alpha) * (
        linear_term * load_factor**2 + K2 * load_factor + Inverse_ter
    )
    return T_W


def Best_L_D_speed(altitude, Cd0, Wing_Loading):  ### best lift to drag speed
    K = Aircraft.Aerodynamics.K1.value
    return np.sqrt(
        (2 / (Atmosphere(altitude).density_slug_ft3.value))
        * Wing_Loading
        * np.sqrt(K / (Cd0 * 3))
    )


def iter_best_L_D_speed(altitude, Wing_Loading):
    # print("getting best L/D speed...")
    ### best lift to drag speed
    tolerance = 1e-3
    max_iterations = 100
    Mach = 0.5
    for i in range(max_iterations):
        Cd0 = Sizing.aerodynamics.Assumptions.Cd0(Mach, altitude)
        speed = Best_L_D_speed(altitude, Cd0, Wing_Loading)
        new_Mach = utils.KEAS_to_Mach(speed, altitude)
        if np.all(abs(new_Mach - Mach) < tolerance):
            print("Speed: ", utils.fts_to_knots(speed))
            break
        Mach = new_Mach
    return utils.fts_to_knots(speed)
