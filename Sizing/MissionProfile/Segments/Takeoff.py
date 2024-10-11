from Sizing.Variable_info.Variable import Variable
import Sizing.utils.utils as utils
import Sizing.aerodynamics.Assumptions as aerodynamics
import Sizing.propulsion.assumptions as propulsion
from Sizing.utils.atmosphere import Atmosphere
import numpy as np
import Sizing.utils.Constants as const
import Sizing.utils.utils as utils


class Takeoff:
    """
    Represents the takeoff segment of a mission profile.
    Attributes:
        takeoff_distance (Variable): The distance required for takeoff, in feet.
        weight_fraction (Variable): The weight fraction (beta) during takeoff.
        obstacle_height (Variable): The height of the obstacle to clear during takeoff, in feet.
    Args:
        takeoff_distance (float): The distance required for takeoff, in feet.
        weight_fraction (float): The weight fraction (beta) during takeoff.
        obstacle_height (Variable, optional): The height of the obstacle to clear during takeoff, in feet. Defaults to 35 feet.
    """

    def __init__(
        self,
        takeoff_distance,
        weight_fraction,
        obstacle_height=35,
        mu=0.05,
        Cd_r=0.07,
        Cl_max=2.56,
        kt0=1.2,
        altitude_runway=0,
        tr=3,
    ):
        self.takeoff_distance = Variable(
            "takeoff_distance", takeoff_distance, "ft", "Takeoff distance"
        )

        self.weight_fraction = Variable(
            "weight_fraction", weight_fraction, "", "Weight fraction (beta)"
        )
        self.obstacle_height = Variable(
            "obstacle_height", obstacle_height, "ft", "Height of obstacle"
        )
        self.mu = Variable("mu", mu, "", "Friction coefficient")
        self.Cd_r = Variable("Cd_r", Cd_r, "", "Rolling drag coefficient")
        self.Cl_max = Variable("Cl_max", Cl_max, "", "Max lift coefficient")
        self.kt0 = Variable("kt0", kt0, "", "Takeoff speed factor")
        self.altitude_runway = Variable(
            "altitude_runway", altitude_runway, "ft", "Altitude of the runway"
        )
        self.tr = Variable("tr", tr, "", "Roration Time")

    @property
    def Cl(self):
        return Variable(
            "Cl", self.Cl_max.value / self.kt0.value**2, "", "Lift coefficient"
        )

    def Cd(self, Mach, altitude):
        return (
            aerodynamics.Cd0(Mach, altitude)
            + self.Cl.value**2 * aerodynamics.K1
            + aerodynamics.K2 * self.Cl.value
        )

    def takeoff_EAS_speed(self, Wing_loading):
        """
        Calculate the takeoff speed.
        Parameters:
        Clmax (float): Maximum lift coefficient.
        Wing_loading (float): Wing loading.
        kt0 (float): Takeoff speed factor.
        altitude (float, optional): Altitude in feet. Default is 0 feet.
        Returns:
        float: Takeoff speed in knots.
        """
        beta = self.weight_fraction.value
        atm = Atmosphere(0)
        rho_0 = atm.density_slug_ft3.value
        Vt0 = np.sqrt(
            (self.kt0.value**2 * 2 * beta * Wing_loading) / (rho_0 * self.Cl_max.value)
        )
        return utils.fts_to_knots(Vt0)

    def ksi(self, Wing_loading):
        return (
            self.Cd(
                utils.KEAS_to_Mach(
                    self.takeoff_EAS_speed(Wing_loading), self.altitude_runway.value
                ),
                self.altitude_runway.value,
            )
            + self.Cd_r.value
            - self.mu.value * self.Cl.value
        )

    def __Mach__(self, wing_loading):
        return utils.KEAS_to_Mach(
            self.takeoff_EAS_speed(wing_loading), self.altitude_runway.value
        )

    def __alpha__(self, wing_loading):
        return propulsion.thrust_lapse(
            self.__Mach__(wing_loading),
            Atmosphere(self.altitude_runway.value).density_ratio.value,
        )

    def tsfc(self, wing_loading):
        return propulsion.TSFC(
            self.__Mach__(wing_loading),
            Atmosphere(self.altitude_runway.value).temperature_ratio.value,
        )

    ## Constraint Analysis
    ### Slide 19
    def Thrust_weight_ratio(
        self,
        Wing_loading,
    ):
        """
        Calculate the thrust-to-weight ratio for takeoff.
        Parameters:
        beta (float): Weight fraction.
        Clmax (float): Maximum lift coefficient.
        Wing_loading (float): Wing loading.
        sg (float, optional): Ground roll distance in feet. Default is 5500 feet.
        altitude (float, optional): Altitude in feet. Default is 0 feet.
        kt0 (float, optional): Takeoff speed factor. Default is 1.2.
        Cl_max (float, optional): Maximum lift coefficient during takeoff. Default is 2.56.
        tr (float, optional): Thrust ratio. Default is 3.
        hobst (float, optional): Obstacle height in feet. Default is 35 feet.
        Returns:
        float: Thrust-to-weight ratio required for takeoff.
        """
        print("Taking off...")
        altitude = self.altitude_runway.value
        kt0 = self.kt0.value
        beta = self.weight_fraction.value
        Clmax = self.Cl_max.value
        tr = self.tr.value
        hobst = self.obstacle_height.value
        st0 = self.takeoff_distance.value
        atm = Atmosphere(altitude)
        rho = atm.density_slug_ft3.value
        alpha = propulsion.thrust_lapse(0, atm.density_ratio.value)
        # alpha = 0.8875
        # rho = 0.002047
        # rho  # Convert from slug/ft^3 to kg/m^3
        Vt0 = np.sqrt((kt0**2 * 2 * beta * Wing_loading) / (rho * Clmax))
        sr = tr * Vt0
        Rc = Vt0**2 / ((0.8 * kt0**2 - 1) * const.SL_GRAVITY_FT)
        theta_obs = np.arccos(1 - hobst / Rc)
        s_obst = Rc * np.sin(theta_obs)
        sg_time_thrust_ratio = (beta**2 * kt0**2 * Wing_loading) / (
            alpha * rho * Clmax * const.SL_GRAVITY_FT
        )
        return sg_time_thrust_ratio / (st0 - s_obst - sr)

    ### Mission Analysis

    def wf_wi(self, WSR, TWR):
        """
        Calculate the weight fraction during the takeoff phase of a mission.
        Parameters:
        WSR (float): Wing loading ratio.
        TWR (float): Thrust-to-weight ratio.
        Mission (Mission_segments.Takeoff): An instance of the Takeoff segment containing mission-specific parameters.
        Returns:
        float: The weight fraction after the takeoff phase. Wendtakeoff/Wstart
        The function takes into account the acceleration and rotation segments of the takeoff phase.
        """

        ### Acceleration segment ###
        old_beta = self.weight_fraction.value
        alt = self.altitude_runway.value
        tsfc = self.tsfc(WSR)
        Vt0 = self.takeoff_EAS_speed(WSR)

        alpha = self.__alpha__(WSR)
        u = (self.ksi(WSR) / self.Cl.value + self.mu.value) * (old_beta / (alpha * TWR))
        WF_over_WI_accel = np.exp(
            -tsfc / const.SL_GRAVITY_FT * (utils.knots_to_fts(Vt0) / (1 - u))
        )

        #### Rotation###
        new_beta = old_beta * WF_over_WI_accel
        Pi_rotation = 1 - tsfc * alpha / new_beta * TWR * self.tr.value
        return Pi_rotation * WF_over_WI_accel
