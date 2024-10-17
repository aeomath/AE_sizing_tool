from Sizing.Variable_info.Variable import Variable

"""
This module defines the `acceleration` class, which models the acceleration or deceleration segment of a mission profile.
Classes:
    acceleration: Represents an acceleration or deceleration segment in a mission profile.
Methods:
    __init__(self, KEAS_start, KEAS_end, time, weight_fraction, altitude, phase_number=-1, name=None):
        Initializes the acceleration or deceleration segment with the given parameters.
    is_deceleration(self):
        Determines if the segment is a deceleration based on the start and end KEAS values.
    Mach_start(self):
        Computes the Mach number at the start of the acceleration.
    Mach_end(self):
        Computes the Mach number at the end of the acceleration.
    tsfc(self, wing_loading):
        Computes the thrust specific fuel consumption (TSFC) for the segment.
    thrust_lapse(self):
        Computes the thrust lapse for the segment.
    Cl(self, wing_loading):
        Computes the lift coefficient (Cl) for the segment.
    Cd0(self):
        Computes the zero-lift drag coefficient (Cd0) for the segment.
    Cd(self, wing_loading):
        Computes the drag coefficient (Cd) for the segment.
    u(self, wing_loading, TWR):
        Computes the non-dimensional parameter u for the segment.
    av_acceleration(self):
        Computes the average acceleration for the segment.
    Thrust_Weight_Ratio(self, wing_loading):
        Computes the thrust-to-weight ratio required for the segment.
    wf_wi(self, WSR, TWR):
        Computes the weight fraction for the segment.
    alpha_seg(self, WSR):
        Computes the thrust lapse for the segment.
    lift_drag_ratio(self, wing_loading):
        Computes the lift-to-drag ratio for the segment.
"""
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
        if KEAS_start < KEAS_end:
            super().__init__(
                "Acceleration",
                phase_number=phase_number,
                weight_fraction=weight_fraction,
                name=name,
            )
        else:
            super().__init__(
                "Deceleration",
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

    def tsfc(self, wing_loading):
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
        """
        Calculate the thrust-to-weight ratio for a given wing loading.
        This method computes the thrust-to-weight ratio based on the wing loading,
        aerodynamic coefficients, and other mission profile parameters. It accounts
        for different phases of flight, including acceleration and deceleration.
        See Section VI.D of the Sizing Report for more details.
        Parameters:
        -----------
        wing_loading : float
            The wing loading value (weight per unit wing area).
        Returns:
        --------
        float
            The calculated thrust-to-weight ratio. Returns 0 if the phase is a deceleration phase.
        Notes:
        ------
        - The method uses several aerodynamic constants (K1, K2) and mission profile parameters
          such as weight fraction, altitude, and equivalent airspeed (EAS) at the start and end
          of the segment.
        - The dynamic pressure (q) is averaged between the start and end of the segment.
        - The method also considers the drag coefficient (Cd0) and thrust lapse rate (alpha).
        - The thrust-to-weight ratio is adjusted for the average acceleration during the segment.
        """

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
        """
        Calculate the weight fraction (wf/wi) for the acceleration segment.
        This method computes the weight fraction for an acceleration segment
        based on the Wing Loading (WSR) and Thrust-to-Weight Ratio (TWR).
        If the segment is a deceleration phase, it returns 1 as no fuel is burned.
        See Section V.D and V.G of the Sizing Report for more details.
        Parameters:
        WSR (float): Wing Loading Ratio.
        TWR (float): Thrust-to-Weight Ratio.
        Returns:
        float: The weight fraction for the acceleration segment.
        """

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
        return np.exp(-self.tsfc(WSR) / V * delta_V / (1 - self.u(WSR, TWR)))

    def alpha_seg(self, WSR):
        return self.thrust_lapse()

    def lift_drag_ratio(self, wing_loading):
        return self.Cl(wing_loading) / self.Cd(wing_loading)
