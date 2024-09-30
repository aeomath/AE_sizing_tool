from Sizing.Variable_info.Variable import Variable


"""
This code defines the variables used in the aircraft sizing project, Those of the varaiable used
to design aircraft. Once the aircraft is fixed, they are fixed.
- `Aircraft` class represents the aircraft and contains nested classes for different components.
- `Design` class represents the design variables of the aircraft.

Author: Adam Benabou 
"""


class Aircraft:
    class Design:
        TOW = Variable("TOW", 1, "kg", description="Takeoff weight")
        WING_LOADING = Variable(
            "wing_loading", unit="kg/m^2", description="Wing loading of the aircraft"
        )
        THRUST_TO_WEIGHT = Variable(
            "thrust_to_weight", unit="", description="Thrust to weight ratio"
        )
        Wing_Area = Variable("Wing_Area", 1, "m^2", description="Wing Area")
        Weight_fractions = Variable(
            "Weight_fractions",
            value=[],
            unit="",
            description="Weight fractions of the aircraft",
        )

    class Aerodynamics:
        K1 = Variable(
            "K1",
            value=0.0556,
            unit="",
            description="Induced drag factor (square of lift coefficient)",
        )
        K2 = Variable("K2", value=-0.0197, unit="", description="Induced drag factor")
        K_we = Variable(
            "K_we",
            value=0.04,
            unit="",
            description="empirrical factor for wing weight fraction",
        )

    class Propulsion:
        ktsfc = Variable(
            "ktsfc",
            value=0.64,
            unit="",
            description="kTSFC is a technology factor for fuel flow applied on Mattingly’s equation",
        )
