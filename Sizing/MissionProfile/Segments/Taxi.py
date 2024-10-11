from Sizing.Variable_info.Variable import Variable
import Sizing.utils.utils as utils
import Sizing.propulsion.assumptions as propulsion
from Sizing.utils.atmosphere import Atmosphere


class Taxi:
    def __init__(
        self, time, percent_fuel_flow, weight_fraction=1, taxi_speed=15, altitude=0
    ):
        self.time = Variable("time", time, "min", "Time of taxi")
        self.percent_fuel_flow = Variable(
            "percent_fuel_flow",
            percent_fuel_flow,
            "",
            "Percent of takeoff fuel flow used during taxi",
        )
        self.speed = Variable(
            "taxi_speed", taxi_speed, "knots", "Taxi speed"
        )  ## Assumed to be at sea level
        self.weight_fraction = Variable(
            "weight_fraction", weight_fraction, "", "Weight fraction (beta)"
        )
        self.altitude = Variable("altitude", altitude, "ft", "Altitude")

    def Mach(self):
        return utils.TAS_to_Mach(self.speed.value, self.altitude.value)

    def tsfc(self):
        return propulsion.TSFC(
            self.Mach(), Atmosphere(self.altitude.value).temperature_ratio.value
        )

    def thrust_lapse(self):
        return propulsion.thrust_lapse(
            self.Mach(), Atmosphere(self.altitude.value).density_ratio.value
        )

    def wf_wi(self, TWR):
        return (
            1
            - self.tsfc()
            * self.percent_fuel_flow.value
            * TWR
            * self.time.value
            * 60
            * self.thrust_lapse()
            / self.weight_fraction.value
        )
