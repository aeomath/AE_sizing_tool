from Sizing.Variable_info.Variable import Variable

"""
This module defines the Taxi class, which models the taxiing segment of an aircraft's mission profile.
Classes:
    Taxi: Represents the taxiing phase of an aircraft's mission profile.
Methods:
    __init__(self, time, percent_fuel_flow, weight_fraction=1, speed=15, altitude=0, phase_number=-1, name=None):
        Initializes the Taxi segment with the given parameters.
    Mach(self):
        Calculates the Mach number based on the taxi speed and altitude.
    tsfc(self, wing_loading):
        Calculates the thrust specific fuel consumption (TSFC) for the taxi segment.
    thrust_lapse(self):
        Calculates the thrust lapse rate for the taxi segment.
    q(self):
        Calculates the dynamic pressure during the taxi segment.
    Cl(self, wing_loading=None):
        Returns the lift coefficient, which is zero for the taxi segment.
    Cd(self, wing_loading):
        Returns the drag coefficient, which is zero for the taxi segment.
    wf_wi(self, WSR, TWR):
        Calculates the weight fraction after the taxi segment.
    Cd0(self):
        Calculates the zero-lift drag coefficient for the taxi segment.
    Thrust_Weight_Ratio(self, WSR):
        Returns the thrust-to-weight ratio, which is zero for the taxi segment.
    alpha_seg(self, WSR):
        Calculates the alpha segment value, assuming 20% of the fuel flow is used during taxi.
"""
import Sizing.utils.utils as utils
import Sizing.propulsion.assumptions as propulsion
import Sizing.aerodynamics.Assumptions as aerodynamics
from Sizing.utils.atmosphere import Atmosphere
from Sizing.MissionProfile.segments import segments
from Sizing.Variable_info.variables import Aircraft


class Taxi(segments):
    def __init__(
        self,
        time,
        percent_fuel_flow,
        weight_fraction=1,
        speed=15,  ## Speed of taxi assumed to be 15 knots EAS
        altitude=0,
        phase_number=-1,
        name=None,
    ):
        super().__init__(
            "Taxi,",
            phase_number=phase_number,
            weight_fraction=weight_fraction,
            name=name,
        )
        self.time = Variable("time", time, "min", "Time of taxi")
        self.percent_fuel_flow = Variable(
            "percent_fuel_flow",
            percent_fuel_flow,
            "",
            "Percent of takeoff fuel flow used during taxi",
        )
        self.speed = Variable(
            "taxi_speed", speed, "knots", "Taxi speed"
        )  ## Assumed to be at sea level
        self.altitude = Variable("altitude", altitude, "ft", "Altitude")

    def Mach(self):
        return utils.TAS_to_Mach(self.speed.value, self.altitude.value)

    def tsfc(self, wing_loading):
        return propulsion.TSFC(
            self.Mach(), Atmosphere(self.altitude.value).temperature_ratio.value
        )

    def thrust_lapse(self):
        return propulsion.thrust_lapse(
            self.Mach(), Atmosphere(self.altitude.value).density_ratio.value
        )

    def q(self):
        return (
            0.5
            * Atmosphere(0).density_slug_ft3.value
            * utils.knots_to_fts(self.speed.value) ** 2
        )

    def Cl(self, wing_loading=None):
        return 0  ## No lift required for taxi segment

    def Cd(self, wing_loading):
        return 0  ## No drag required for taxi segment

    def wf_wi(self, WSR, TWR):
        """
        Calculate the weight fraction for a given wing loading and thrust-to-weight ratio.
        Parameters:
        WSR (float): Wing loading (weight per unit area of the wing).
        TWR (float): Thrust-to-weight ratio.
        Returns:
        float: The calculated weight fraction.
        See section V.A of the report for more details.
        """

        return (
            1
            - self.tsfc(wing_loading=WSR)
            * self.percent_fuel_flow.value
            * TWR
            * self.time.value
            * 60
            * self.thrust_lapse()
            / self.weight_fraction.value
        )

    def Cd0(self):
        return aerodynamics.Cd0(self.Mach(), self.altitude.value)

    def Thrust_Weight_Ratio(self, WSR):
        return 0 * WSR  ## We assume no constraints for taxi segment

    def alpha_seg(self, WSR):
        ## Assumed that only 20 % of the fuel flow is used during taxi
        return self.thrust_lapse() * self.percent_fuel_flow.value
