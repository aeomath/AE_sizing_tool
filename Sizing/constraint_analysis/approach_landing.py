from Sizing.Variable_info.Variable import Variable
import Sizing.aerodynamics
import Sizing.aerodynamics.Assumptions


from Sizing.MissionProfile.Segments import Mission_segments
from Sizing.utils.atmosphere import Atmosphere
from Sizing.propulsion.assumptions import thrust_lapse, TSFC
import numpy as np
import Sizing.utils.Constants as const
import Sizing.utils.utils as utils
from Sizing.Variable_info.variables import Aircraft
import Sizing


def thrust_weight_ratio_approach(
    wing_loading, mission_segment: Mission_segments.approach
):

    print("Approach segment")
    beta = mission_segment.weight_fraction.value
    speed_EAS = mission_segment.KEAS.value
    start_alt = mission_segment.start_altitude.value
    end_alt = mission_segment.end_altitude.value
    flight_path_angle = mission_segment.flight_path_angle.value

    sigma_start = Atmosphere(start_alt).density_ratio.value
    sigma_end = Atmosphere(end_alt).density_ratio.value
    K1 = Aircraft.Aerodynamics.K1.value
    K2 = Aircraft.Aerodynamics.K2.value

    q = 0.5 * Atmosphere(0).density_slug_ft3.value * utils.knots_to_fts(speed_EAS) ** 2
    Cd0_start = Sizing.aerodynamics.Assumptions.Cd0(
        utils.KEAS_to_Mach(speed_EAS, start_alt), start_alt
    )
    Cd0_end = Sizing.aerodynamics.Assumptions.Cd0(
        utils.KEAS_to_Mach(speed_EAS, end_alt), end_alt
    )
    Cd0 = (Cd0_start + Cd0_end) / 2
    alpha_star = thrust_lapse(utils.KEAS_to_Mach(speed_EAS, start_alt), sigma_start)
    alpha_end = thrust_lapse(utils.KEAS_to_Mach(speed_EAS, end_alt), sigma_end)
    alpha = (alpha_star + alpha_end) / 2

    linear_term = K1 * (beta / q) * wing_loading
    Inverse_ter = Cd0 / ((beta / q) * wing_loading)
    T_W = (beta / alpha) * (
        linear_term + K2 + Inverse_ter + np.sin(flight_path_angle * np.pi / 180)
    )
    return T_W


def landing_constraint(Mission: Mission_segments.landing):
    q = (
        0.5
        * Atmosphere(0).density_slug_ft3.value
        * utils.knots_to_fts(Mission.KEAS.value) ** 2
    )
    Beta = Mission.weight_fraction.value
    return Mission.Cl_max.value * q / Beta
