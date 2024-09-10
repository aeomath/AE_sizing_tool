from Variable import Variable


"""
This code defines the variables used in the aircraft sizing project.
- `Aircraft` class represents the aircraft and contains nested classes for different components.
- `Design` class represents the design variables of the aircraft.

Author: Adam Benabou @aeomath
"""


class Aircraft:
    class Design:
        TOW = Variable("tow", 1, "kg", description="Takeoff weight")
        WING_LOADING = Variable("wing_loading", unit="kg/m^2")
        THRUST_TO_WEIGHT = Variable("thrust_to_weight", 1, "")

    class Wing:
        MASS = Variable("wing_mass", 1, "kg")
        AREA = Variable("wing_area", 1, "m^2")
