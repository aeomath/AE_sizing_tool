from Sizing.Variable_info.Variable import Variable
import Sizing.utils.utils as utils
import Sizing.aerodynamics.Assumptions as aerodynamics
import Sizing.propulsion.assumptions as propulsion
from Sizing.utils.atmosphere import Atmosphere
import numpy as np
import Sizing.utils.Constants as const
from Sizing.MissionProfile.segments import segments


class acceleration(segments):
    def __init__(
        self,
        KEAS_start,
        KEAS_end,
        time,
        weight_fraction,
        altitude,
        phase_number=-1,
        name=None,
    ):
        super().__init__(
            "Acceleration",
            phase_number=phase_number,
            weight_fraction=weight_fraction,
            name=name,
        )
        self.KEAS_start = Variable(
            "KEAS_start", KEAS_start, "KEAS", "Start Equivalent airspeed"
        )
        self.KEAS_end = Variable(
            "KEAS_end", KEAS_end, "KEAS", "End Equivalent airspeed"
        )
        self.time = Variable("time", time, "s", "Time of acceleration")
        self.altitude = Variable("altitude", altitude, "ft", "Altitude")

    def is_deceleration(self):
        return self.KEAS_start.value > self.KEAS_end.value

    @property
    def Mach_start(self):
        return Variable(
            "Mach_start",
            utils.KEAS_to_Mach(self.KEAS_start.value, self.altitude.value),
            "",
            "Start of acceleration Mach number",
        )

    @property
    def Mach_end(self):
        return Variable(
            "Mach_end",
            utils.KEAS_to_Mach(self.KEAS_end.value, self.altitude.value),
            "",
            "End of acceleration Mach number",
        )

    def tsfc(self):
        tsfc_start = propulsion.TSFC(
            self.Mach_start.value,
            Atmosphere(self.altitude.value).temperature_ratio.value,
        )
        tsfc_end = propulsion.TSFC(
            self.Mach_end.value,
            Atmosphere(self.altitude.value).temperature_ratio.value,
        )
        return (tsfc_start + tsfc_end) / 2

    def thrust_lapse(self):
        alpha_start = propulsion.thrust_lapse(
            self.Mach_start.value,
            Atmosphere(self.altitude.value).density_ratio.value,
        )
        alpha_end = propulsion.thrust_lapse(
            self.Mach_end.value, Atmosphere(self.altitude.value).density_ratio.value
        )
        return (alpha_start + alpha_end) / 2

    def Cl(self, wing_loading):
        q_start = (
            0.5
            * Atmosphere(0).density_slug_ft3.value
            * utils.knots_to_fts(self.KEAS_start.value) ** 2
        )
        q_end = (
            0.5
            * Atmosphere(0).density_slug_ft3.value
            * utils.knots_to_fts(self.KEAS_end.value) ** 2
        )
        q = (q_start + q_end) / 2
        return self.weight_fraction.value * wing_loading / q

    def Cd0(self):
        return (
            aerodynamics.Cd0(self.Mach_start.value, self.altitude.value)
            + aerodynamics.Cd0(self.Mach_end.value, self.altitude.value)
        ) / 2

    def Cd(self, wing_loading):
        return (
            self.Cd0()
            + aerodynamics.K1 * self.Cl(wing_loading) ** 2
            + aerodynamics.K2 * self.Cl(wing_loading)
        )

    def u(self, wing_loading, TWR):
        return (self.Cd(wing_loading) * self.weight_fraction.value) / (
            self.thrust_lapse() * self.Cl(wing_loading) * TWR
        )

    ## Constraints ##
    def av_acceleration(self):
        "Compute the average acceleration"
        return utils.knots_to_fts(self.KEAS_end.value - self.KEAS_start.value) / (
            self.time.value * const.SL_GRAVITY_FT
        )

    def Thrust_Weight_Ratio(self, wing_loading):
        if self.is_deceleration():
            # print("Deceleration : no Thrust required for phase", self.phase_number)
            return 0 * wing_loading

        beta = self.weight_fraction.value
        altitude = self.altitude.value
        EAS_Start = self.KEAS_start.value
        EAS_End = self.KEAS_end.value
        K1 = aerodynamics.K1
        K2 = aerodynamics.K2
        q_start = (
            0.5
            * Atmosphere(0).density_slug_ft3.value
            * utils.knots_to_fts(EAS_Start) ** 2
        )
        q_end = (
            0.5
            * Atmosphere(0).density_slug_ft3.value
            * utils.knots_to_fts(EAS_End) ** 2
        )
        q = (q_start + q_end) / 2
        Cd0 = self.Cd0()
        alpha = self.thrust_lapse()
        linear_term = K1 * (beta / q) * wing_loading
        Inverse_term = Cd0 / ((beta / q) * wing_loading)
        T_W = (beta / alpha) * (
            linear_term + K2 + Inverse_term + self.av_acceleration()
        )
        return T_W

    ##Mission analysis###
    def wf_wi(self, WSR, TWR):
        if self.is_deceleration():
            # print("Deceleration : no fuel burned for phase", self.phase_number)
            return 1
        V_start = utils.knots_to_fts(
            utils.KEAS_to_TAS(self.KEAS_start.value, self.altitude.value)
        )
        V_end = utils.knots_to_fts(
            utils.KEAS_to_TAS(self.KEAS_end.value, self.altitude.value)
        )
        V = utils.knots_to_fts(V_start + V_end) / 2
        delta_V = (V_end**2 - V_start**2) / (2 * const.SL_GRAVITY_FT)
        return np.exp(-self.tsfc() / V * delta_V / (1 - self.u(WSR, TWR)))
