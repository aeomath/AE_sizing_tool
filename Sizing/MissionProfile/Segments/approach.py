from Sizing.Variable_info.Variable import Variable
import Sizing.utils.utils as utils
import Sizing.aerodynamics.Assumptions as aerodynamics
import Sizing.propulsion.assumptions as propulsion
from Sizing.utils.atmosphere import Atmosphere
import numpy as np
import Sizing.utils.Constants as const
from Sizing.MissionProfile.segments import segments


class approach(segments):
    def __init__(
        self,
        flight_path_angle,
        start_altitude,
        end_altitude,
        weight_fraction,
        KEAS,
        percent_fuel_flow=0.20,
        phase_number=-1,
        name=None,
        weight_fraction_constraint=0.85,
    ):
        super().__init__(
            "Approach",
            phase_number=phase_number,
            weight_fraction=weight_fraction,
            name=name,
        )
        self.flight_path_angle = Variable(
            "flight_angle", flight_path_angle, "deg", "Flight angle"
        )
        self.start_altitude = Variable(
            "start_altitude", start_altitude, "ft", "Start altitude"
        )
        self.end_altitude = Variable("end_altitude", end_altitude, "ft", "End altitude")
        self.KEAS = Variable("KEAS", KEAS, "KEAS", "Equivalent airspeed")
        self.percent_fuel_flow = Variable(
            "percent_fuel_flow", percent_fuel_flow, "", "Percent fuel flow"
        )
        self.weight_fraction_constraint = Variable(
            "weight_fraction_constraint",
            weight_fraction_constraint,
            "",
            "Weight fraction constraint applied for the approach",
        )

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

    def Thrust_Weight_Ratio(self, wing_loading):
        beta = self.weight_fraction_constraint.value  ## Constraint on weight fraction
        speed_EAS = self.KEAS.value
        flight_path_angle = self.flight_path_angle.value

        K1 = aerodynamics.K1
        K2 = aerodynamics.K2

        q = (
            0.5
            * Atmosphere(0).density_slug_ft3.value
            * utils.knots_to_fts(speed_EAS) ** 2
        )
        Cd0 = self.Cd0()
        alpha = self.percent_fuel_flow.value
        linear_term = K1 * (beta / q) * wing_loading
        Inverse_ter = Cd0 / ((beta / q) * wing_loading)
        T_W = (beta / alpha) * (
            linear_term
            + K2
            + Inverse_ter
            - np.sin(
                flight_path_angle * np.pi / 180
            )  ## negative sign because the flight path angle is negative (descending), input is positive
        )
        return T_W

    def Cl(self, wing_loading):
        q = (
            0.5
            * Atmosphere(0).density_slug_ft3.value
            * utils.knots_to_fts(self.KEAS.value) ** 2
        )
        return (
            wing_loading
            * self.weight_fraction.value
            # * np.cos(-self.flight_path_angle.value * np.pi / 180)
        ) / q

    def Cd(self, wing_loading):
        return (
            self.Cd0()
            + aerodynamics.K1 * self.Cl(wing_loading) ** 2
            + aerodynamics.K2 * self.Cl(wing_loading)
        )

    def u(self, wing_loading, TWR):
        return (self.Cd(wing_loading) * self.weight_fraction.value) / (
            self.alpha() * self.percent_fuel_flow.value * self.Cl(wing_loading) * TWR
        )

    def tsfc(self, wing_loading):
        tsfc_start = propulsion.TSFC(
            utils.KEAS_to_Mach(self.KEAS.value, self.start_altitude.value),
            Atmosphere(self.start_altitude.value).temperature_ratio.value,
        )
        tsfc_end = propulsion.TSFC(
            utils.KEAS_to_Mach(self.KEAS.value, self.end_altitude.value),
            Atmosphere(self.end_altitude.value).temperature_ratio.value,
        )
        return (tsfc_start + tsfc_end) / 2

    def TAS_knots(self):
        TAS_start = utils.KEAS_to_TAS(self.KEAS.value, self.start_altitude.value)
        TAS_end = utils.KEAS_to_TAS(self.KEAS.value, self.end_altitude.value)
        return (TAS_start + TAS_end) / 2  # Average TAS in knots

    def delta_t(self):
        TAS = utils.knots_to_fts(self.TAS_knots())
        "" "Estimation of time for the approach segment" ""
        delta_h = abs(self.start_altitude.value - self.end_altitude.value)
        return delta_h / (TAS * np.sin(self.flight_path_angle.value * np.pi / 180))

    def wf_wi(self, WSR, TWR):
        """
        Calculate the weight fraction during the approach phase of a mission.
        Parameters:
        WSR (float): Wing loading ratio.
        TWR (float): Thrust-to-weight ratio.
        Mission (Mission_segments.climb): An instance of the approach segment containing mission-specific parameters.
        Returns:
        float: The weight fraction after the climb phase. Wendclimb/Wstart
        The function takes into account the climb segment of the mission.
        """
        alpha = self.alpha()
        beta = self.weight_fraction.value
        return np.exp(-self.tsfc(WSR) * alpha / beta * TWR * self.delta_t())

    def alpha_seg(self, WSR):
        return self.alpha()

    def lift_drag_ratio(self, wing_loading):
        return self.Cl(wing_loading) / self.Cd(wing_loading)
