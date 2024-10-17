from Sizing.Variable_info.Variable import Variable
import Sizing.utils.utils as utils
import Sizing.aerodynamics.Assumptions as aerodynamics
import Sizing.propulsion.assumptions as propulsion
from Sizing.utils.atmosphere import Atmosphere
import numpy as np
import Sizing.utils.Constants as const
from Sizing.MissionProfile.segments import segments
from Sizing.Variable_info.variables import Aircraft


class climb(segments):
    """
    This class contains the variables for the climb and descent segments of the mission profile.
    If climb, climb_rate is positive, else if descent, climb_rate is negative.
    Attributes:
        climb_rate (Variable): Rate of climb in ft/min.
        KEAS (Variable): Equivalent airspeed . If none, Climb is at constant Mach number.
        MACH (Variable): Mach number. if none, Climb is at constant EAS.
        start_altitude (Variable): Start altitude.
        end_altitude (Variable): End altitude.
        time (Variable): Time of climb.
        weight_fraction (Variable): Weight fraction (beta) at the end of the phase.

    """

    def __init__(
        self,
        start_altitude,
        end_altitude,
        time,
        weight_fraction,
        KEAS=None,
        MACH=None,
        climb_rate=None,
        flight_path_angle=None,
        phase_number=-1,
        name=None,
        is_additional_constraint=False,
    ):
        ### Check that either Mach or EAS is provided
        if KEAS is None and MACH is None:
            raise ValueError("Either Mach or EAS must be provided")
        if KEAS is not None and MACH is not None:
            raise ValueError("Either Mach or EAS must be provided")
        ## Check that either flight path angle or ROC is provided
        if climb_rate is None and flight_path_angle is None:
            raise ValueError("Either climb rate or flight path angle must be provided")
        if climb_rate is not None and flight_path_angle is not None:
            raise ValueError("Either climb rate or flight path angle must be provided")
        if climb_rate is not None:
            if climb_rate < 0:
                super().__init__(
                    "Descent",
                    phase_number=phase_number,
                    weight_fraction=weight_fraction,
                    name=name,
                )
            else:
                super().__init__(
                    "Climb",
                    phase_number=phase_number,
                    weight_fraction=weight_fraction,
                    name=name,
                )
        elif flight_path_angle is not None:
            if flight_path_angle < 0:
                super().__init__(
                    "Descent",
                    phase_number=phase_number,
                    weight_fraction=weight_fraction,
                    name=name,
                )
            else:
                super().__init__(
                    "Climb",
                    phase_number=phase_number,
                    weight_fraction=weight_fraction,
                    name=name,
                )

        self.KEAS = Variable("KEAS", KEAS, "KEAS", "Equivalent airspeed")
        self.MACH = Variable("MACH", MACH, "", "Mach number")
        self.climb_rate = Variable("climb_rate", climb_rate, "m/s", "Rate of climb")
        self.flight_path_angle = Variable(
            "flight_path_angle", flight_path_angle, "deg", "Flight path angle"
        )
        self.start_altitude = Variable(
            "start_altitude", start_altitude, "ft", "Start altitude"
        )
        self.end_altitude = Variable("end_altitude", end_altitude, "ft", "End altitude")
        self.time = Variable("time", time, "s", "Time of climb")
        self.is_additional_constraint = is_additional_constraint

    def Cl(self, wing_loading):
        """
        Calculate the lift coefficient (Cl) for a given wing loading.
        Parameters:
        wing_loading (float): The wing loading value (weight per unit area).

        Returns:
        float: The calculated lift coefficient (Cl).

        If mach is provided, Cl is averaged between start and end altitude
        """
        if self.KEAS.value is not None:
            q = (
                0.5
                * Atmosphere(0).density_slug_ft3.value
                * utils.knots_to_fts(self.KEAS.value) ** 2
            )

        elif self.MACH.value is not None:
            q_start = (
                0.5
                * Atmosphere(0).density_slug_ft3.value
                * utils.knots_to_fts(
                    utils.Mach_to_KEAS(self.MACH.value, self.start_altitude.value)
                )
                ** 2
            )
            q_end = (
                0.5
                * Atmosphere(0).density_slug_ft3.value
                * utils.knots_to_fts(
                    utils.Mach_to_KEAS(self.MACH.value, self.end_altitude.value)
                )
                ** 2
            )
            q = (q_start + q_end) / 2
        return self.weight_fraction.value * wing_loading / q

    def thrust_lapse(self):
        """
        Calculate the average thrust lapse between start and end altitude.
        Returns:
        float: The average thrust lapse ratio.
        """
        start_alt = self.start_altitude.value
        end_alt = self.end_altitude.value
        sigma_start = Atmosphere(start_alt).density_ratio.value
        sigma_end = Atmosphere(end_alt).density_ratio.value
        if self.MACH.value is not None:
            alpha_start = propulsion.thrust_lapse(self.MACH.value, sigma_start)
            alpha_end = propulsion.thrust_lapse(self.MACH.value, sigma_end)
        elif self.KEAS.value is not None:
            alpha_start = propulsion.thrust_lapse(
                utils.KEAS_to_Mach(self.KEAS.value, start_alt), sigma_start
            )
            alpha_end = propulsion.thrust_lapse(
                utils.KEAS_to_Mach(self.KEAS.value, end_alt), sigma_end
            )
        return (alpha_start + alpha_end) / 2

    def Cd0(self):
        """
        Calculate the average zero-lift drag coefficient between start and end altitude.
        Returns:
        float: The average zero-lift drag coefficient.
        """
        start_alt = self.start_altitude.value
        end_alt = self.end_altitude.value
        if self.MACH.value is not None:
            Cd0_start = aerodynamics.Cd0(self.MACH.value, start_alt)
            Cd0_end = aerodynamics.Cd0(self.MACH.value, end_alt)
        elif self.KEAS.value is not None:
            Cd0_start = aerodynamics.Cd0(
                utils.KEAS_to_Mach(self.KEAS.value, start_alt), start_alt
            )
            Cd0_end = aerodynamics.Cd0(
                utils.KEAS_to_Mach(self.KEAS.value, end_alt), end_alt
            )
        return (Cd0_start + Cd0_end) / 2

    def Cd(self, wing_loading):
        return (
            self.Cd0()
            + self.Cl(wing_loading) ** 2 * aerodynamics.K1
            + aerodynamics.K2 * self.Cl(wing_loading)
        )

    def u(self, wing_loading, TWR):
        return (self.Cd(wing_loading) * self.weight_fraction.value) / (
            self.thrust_lapse() * self.Cl(wing_loading) * TWR
        )

    def tsfc(self, wing_loading):
        """
        Calculate the average thrust-specific fuel consumption (TSFC) between start and end altitude.
        Returns:
            float: The average TSFC for the segment.

        """

        if self.MACH.value is not None:
            tsfc_start = propulsion.TSFC(
                self.MACH.value,
                Atmosphere(self.start_altitude.value).temperature_ratio.value,
            )
            tsfc_end = propulsion.TSFC(
                self.MACH.value,
                Atmosphere(self.end_altitude.value).temperature_ratio.value,
            )
        elif self.KEAS.value is not None:
            tsfc_start = propulsion.TSFC(
                utils.KEAS_to_Mach(self.KEAS.value, self.start_altitude.value),
                Atmosphere(self.start_altitude.value).temperature_ratio.value,
            )
            tsfc_end = propulsion.TSFC(
                utils.KEAS_to_Mach(self.KEAS.value, self.end_altitude.value),
                Atmosphere(self.end_altitude.value).temperature_ratio.value,
            )
        return (tsfc_start + tsfc_end) / 2

    def is_accurate(self, wing_loading, TWR):
        """
        Check if we values can be averaged for the altitude interval used in the analysis although the variance in the quantity
        """
        temp_ratio_start = Atmosphere(self.start_altitude.value).temperature_ratio.value
        temp_ratio_end = Atmosphere(self.end_altitude.value).temperature_ratio.value
        temp_ratio = (temp_ratio_start + temp_ratio_end) / 2
        print(np.sqrt(temp_ratio) / (1 - self.u(wing_loading, TWR)))
        return np.sqrt(temp_ratio) / (1 - self.u(wing_loading, TWR))

    ### Constraint_analysis
    def Thrust_Weight_Ratio(self, wing_loading):
        """
        Calculate the thrust-to-weight ratio for climb.
        2 cases are considered:
        1. Climb at constant Mach number
        2. Climb at constant equivalent airspeed (EAS)
        see Section VI.C of the Sizing Report for more details.
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
        start_alt = self.start_altitude.value
        end_alt = self.end_altitude.value
        beta = self.weight_fraction.value
        ROC = self.climb_rate.value
        K1 = aerodynamics.K1
        K2 = aerodynamics.K2
        Cd0 = self.Cd0()
        alpha = self.thrust_lapse()
        # Case 1: Climb at constant Mach number
        if self.MACH.value is not None:
            ### Climb at constant Mach number ,q is averaged between start and end altitude
            q_start = (
                0.5
                * Atmosphere(0).density_slug_ft3.value
                * utils.knots_to_fts(utils.Mach_to_KEAS(self.MACH.value, start_alt))
                ** 2
            )
            q_end = (
                0.5
                * Atmosphere(0).density_slug_ft3.value
                * utils.knots_to_fts(utils.Mach_to_KEAS(self.MACH.value, end_alt)) ** 2
            )
            q = (q_start + q_end) / 2
            ## if flight path angle is not given, use the rate of climb to calculate the climb term
            if ROC is not None:
                V_start = utils.Mach_to_TAS(self.MACH.value, start_alt)
                V_end = utils.Mach_to_TAS(self.MACH.value, end_alt)
                V = utils.knots_to_fts((V_end + V_start / 2))
                climb_term = (ROC / 60) / V
            ## if flight path angle is given, use it to calculate the climb term
            elif self.flight_path_angle is not None:
                climb_term = np.sin(self.flight_path_angle * np.pi / 180)

        # Case 2: Climb at constant equivalent airspeed (EAS)
        if self.KEAS.value is not None:
            ### Climb at constant EAS speed
            q = (
                0.5
                * Atmosphere(0).density_slug_ft3.value
                * utils.knots_to_fts(self.KEAS.value) ** 2
            )
            ### if flight path angle is not given, use the rate of climb to calculate the climb term
            if ROC is not None:
                V_start = utils.KEAS_to_TAS(
                    self.KEAS.value, start_alt
                )  ### TAS  is in knots
                V_end = utils.KEAS_to_TAS(self.KEAS.value, end_alt)

                V = utils.knots_to_fts((V_start + V_end) / 2)
                climb_term = (ROC / 60) / V  ### ROC is in ft/min so convert to ft/s
            ## if flight path angle is given, use it to calculate the climb term
            elif self.flight_path_angle.value is not None:
                climb_term = np.sin(self.flight_path_angle.value * np.pi / 180)
        linear_term = K1 * (beta / q) * wing_loading
        Inverse_ter = Cd0 / ((beta / q) * wing_loading)
        T_W = (beta / alpha) * (linear_term + K2 + Inverse_ter + climb_term)
        # print(self.name, beta)
        if self.type != "Climb":
            return 0 * wing_loading
        return T_W

    ## Override
    def wf_wi(self, WSR, TWR):
        """
        Calculate the weight fraction during the climb phase of a mission.
        Parameters:
        WSR (float): Wing loading ratio.
        TWR (float): Thrust-to-weight ratio.
        Mission (Mission_segments.climb): An instance of the climb segment containing mission-specific parameters.
        Returns:
        float: The weight fraction after the climb phase. Wendclimb/Wstart
        The function takes into account the climb segment of the mission.
        see Section V.C of the Sizing Report for more details.
        """
        if self.is_additional_constraint:
            return 1
        if self.KEAS.value is not None:
            TAS_start = utils.KEAS_to_TAS(self.KEAS.value, self.start_altitude.value)
            TAS_end = utils.KEAS_to_TAS(self.KEAS.value, self.end_altitude.value)
        if self.MACH.value is not None:
            TAS_start = utils.Mach_to_TAS(self.MACH.value, self.start_altitude.value)
            TAS_end = utils.Mach_to_TAS(self.MACH.value, self.end_altitude.value)

        TAS_knots = (TAS_start + TAS_end) / 2  # Average TAS in knots
        u = self.u(WSR, TWR)
        alt_accel_end = self.end_altitude.value + utils.knots_to_fts(TAS_end) ** 2 / (
            2 * const.SL_GRAVITY_FT
        )
        alt_accel_start = self.start_altitude.value + utils.knots_to_fts(
            TAS_start
        ) ** 2 / (2 * const.SL_GRAVITY_FT)
        tsfc = self.tsfc(WSR)
        delta = alt_accel_end - alt_accel_start
        if self.type != "Climb":
            # print("Descending : no fuel burned for phase", self.phase_number)
            return 1
        return np.exp(-tsfc / utils.knots_to_fts(TAS_knots) * delta / (1 - u))

    def alpha_seg(self, WSR):
        """
        Calculate the thrust lapse
        Parameters: Optional
        WSR (float): Weight-to-surface ratio of the aircraft. s
        Returns:
        float: Thrust lapse value.
        """
        return self.thrust_lapse()

    def lift_drag_ratio(self, wing_loading):
        return self.Cl(wing_loading) / self.Cd(wing_loading)
