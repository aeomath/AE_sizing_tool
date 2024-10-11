from Sizing.Variable_info.Variable import Variable
import Sizing.utils.utils as utils
import Sizing.aerodynamics.Assumptions as aerodynamics
import Sizing.propulsion.assumptions as propulsion
from Sizing.utils.atmosphere import Atmosphere
import numpy as np
import Sizing.utils.Constants as const


class approach:
    def __init__(
        self,
        flight_path_angle,
        start_altitude,
        end_altitude,
        weight_fraction,
        KEAS,
    ):
        self.flight_path_angle = Variable(
            "flight_angle", flight_path_angle, "deg", "Flight angle"
        )
        self.start_altitude = Variable(
            "start_altitude", start_altitude, "ft", "Start altitude"
        )
        self.end_altitude = Variable("end_altitude", end_altitude, "ft", "End altitude")
        self.weight_fraction = Variable(
            "weight_fraction", weight_fraction, "", "Weight fraction (beta)"
        )
        self.KEAS = Variable("KEAS", KEAS, "KEAS", "Equivalent airspeed")

    def Cd0(self):
        Cd0_start = aerodynamics.Cd0(
            utils.KEAS_to_Mach(self.KEAS.value, self.start_altitude.value),
            self.start_altitude.value,
        )
        Cd0_end = aerodynamics.Cd0(
            utils.KEAS_to_Mach(self.KEAS.value, self.end_altitude.value),
            self.end_altitude.value,
        )
        return (Cd0_start + Cd0_end) / 2

    def alpha(self):
        alpha_start = propulsion.thrust_lapse(
            utils.KEAS_to_Mach(self.KEAS.value, self.start_altitude.value),
            Atmosphere(self.start_altitude.value).density_ratio.value,
        )
        alpha_end = propulsion.thrust_lapse(
            utils.KEAS_to_Mach(self.KEAS.value, self.end_altitude.value),
            Atmosphere(self.end_altitude.value).density_ratio.value,
        )
        return (alpha_start + alpha_end) / 2

    def thrust_weight_ratio(self, wing_loading):
        print("Approach segment")
        beta = self.weight_fraction.value
        speed_EAS = self.KEAS.value
        start_alt = self.start_altitude.value
        end_alt = self.end_altitude.value
        flight_path_angle = self.flight_path_angle.value

        sigma_start = Atmosphere(start_alt).density_ratio.value
        sigma_end = Atmosphere(end_alt).density_ratio.value
        K1 = aerodynamics.K1
        K2 = aerodynamics.K2

        q = (
            0.5
            * Atmosphere(0).density_slug_ft3.value
            * utils.knots_to_fts(speed_EAS) ** 2
        )
        Cd0 = self.Cd0()
        alpha = self.alpha()
        linear_term = K1 * (beta / q) * wing_loading
        Inverse_ter = Cd0 / ((beta / q) * wing_loading)
        T_W = (beta / alpha) * (
            linear_term
            + K2
            + Inverse_ter
            - np.sin(
                flight_path_angle * np.pi / 180
            )  ## negative sign because the flight path angle is negative (descending)
        )
        return T_W
