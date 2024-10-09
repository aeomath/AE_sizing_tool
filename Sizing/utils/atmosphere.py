import ussa1976 as ussa
from Sizing.Variable_info.Variable import Variable
import numpy as np

### SEA LEVEL VALUES SL = Sea Level values

SL_VALUES = ussa.compute(z=np.array([0]), variables=["t", "p", "rho", "cs"])
SL_TEMPERATURE = SL_VALUES["t"].values
SL_PRESSURE = SL_VALUES["p"].values
SL_DENSITY = SL_VALUES["rho"].values
SL_SOUND_SPEED = SL_VALUES["cs"].values


class Atmosphere:
    def __init__(self, altitude, meter=False):
        """
        Initializes a new instance of the Atmosphere class.

        Args:
            altitude (float): The altitude of the aircraft in ft .
            meter (bool, optional): True if the altitude is in meters, False if it is in feet. Defaults to False.
        """
        self.meter = meter
        self.altitude = altitude

    @property
    def altitude(self):
        return self._altitude

    @altitude.setter
    def altitude(
        self,
        value,
    ):
        #### Careful , there is a conversion from meters to feet here !!
        if self.meter:
            self._altitude = Variable(
                "altitude", value, "m", "Altitude of the aircraft"
            )
        else:
            self._altitude = Variable(
                "altitude", value * 0.3048, "m", "Altitude of the aircraft"
            )

    ### Add the following properties to the Atmosphere class using the @property decorator and ussa1976 package

    @property
    def temperature(self):
        """
        This function calculates the temperature of the atmosphere based on the altitude.
        Returns:
            float: Temperature of the atmosphere.
        """
        temperature = ussa.compute(
            variables=["t"],
            z=np.array([self.altitude.value]),
        )
        return Variable(
            "temperature", temperature["t"].values, "K", "Temperature of the atmosphere"
        )

    @property
    def pressure(self):
        """
        This function calculates the pressure of the atmosphere based on the altitude.
        Returns:
            float: Pressure of the atmosphere.
        """
        pressure = ussa.compute(
            variables=["p"],
            z=np.array([self.altitude.value]),
        )
        return Variable("pressure", pressure["p"].values, "Pa", "Pressure")

    @property
    def density(self):
        """
        This function calculates the density of the atmosphere based on the altitude.
        Returns:
            float: Density of the atmosphere.
        """
        density = ussa.compute(
            variables=["rho"],
            z=np.array([self.altitude.value]),
        )
        return Variable("density", density["rho"].values, "kg/m^3", "Density")

    @property
    def density_slug_ft3(self):
        """
        This function calculates the density of the atmosphere based on the altitude in slug/ft^3.
        Returns:
            float: Density of the atmosphere in slug/ft^3.
        """
        return Variable(
            "density_slug_ft3",
            self.density.value * 0.0019403203259304,
            "slug/ft^3",
            "Density in slug/ft^3",
        )

    @property
    def speed_of_sound(self):
        """
        This function calculates the speed of sound at the given altitude.
        Returns:
            float: Speed of sound.
        """
        return Variable(
            "speed_of_sound",
            ussa.compute(
                variables=["cs"],
                z=np.array([self.altitude.value]),
            )["cs"].values,
            "m/s",
            "Speed of sound",
        )

    @property
    def density_ratio(self):
        """
        This function calculates the density ratio of the atmosphere based on the altitude.
        Returns:
            float: Density ratio of the atmosphere.
        """
        return Variable(
            "density_ratio",
            self.density.value / SL_DENSITY,
            "",
            "Density ratio of the atmosphere",
        )

    @property
    def pressure_ratio(self):
        """
        This function calculates the pressure ratio of the atmosphere based on the altitude.
        Returns:
            float: Pressure ratio of the atmosphere.
        """
        return Variable(
            "pressure_ratio",
            self.pressure.value / SL_PRESSURE,
            "",
            "Pressure ratio of the atmosphere",
        )

    @property
    def temperature_ratio(self):
        """
        This function calculates the temperature ratio of the atmosphere based on the altitude.
        Returns:
            float: Temperature ratio of the atmosphere.
        """
        return Variable(
            "temperature_ratio",
            self.temperature.value / SL_TEMPERATURE,
            "",
            "Temperature ratio of the atmosphere",
        )
