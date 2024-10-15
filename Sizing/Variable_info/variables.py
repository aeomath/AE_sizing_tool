from Sizing.Variable_info.Variable import Variable

import os
import json as js

"""
This code defines the variables used in the aircraft sizing project, Those of the varaiable used
to design aircraft. Once the aircraft is fixed, they are fixed.
- `Aircraft` class represents the aircraft and contains nested classes for different components.
- `Design` class represents the design variables of the aircraft.

Author: Adam Benabou 
"""
### Constants
# Get the directory of the current script
current_dir = os.path.dirname(__file__)
# Construct the full path to the JSON file in the Inputs directory
file_path_aero = os.path.join(current_dir, "..", "..", "Inputs", "aerodynamics.json")
# Normalize the path
file_path_aero = os.path.normpath(file_path_aero)
file_path_propulsion = os.path.join(
    current_dir, "..", "..", "Inputs", "Propulsion.json"
)
file_path_propulsion = os.path.normpath(file_path_propulsion)

file_path_structure = os.path.join(current_dir, "..", "..", "Inputs", "structural.json")
file_path_structure = os.path.normpath(file_path_structure)

with open(file_path_aero, "r") as file:
    data_aero = js.load(file)
    K_1 = data_aero["K1"]
    K_2 = data_aero["K2"]

with open(file_path_propulsion, "r") as file:
    data_propulsion = js.load(file)
    ktsfc_value = data_propulsion["kTSFC"]

with open(file_path_structure, "r") as file:
    data_structure = js.load(file)
    K_we_value = data_structure["kWE"]
# Data for payload

file_path_payload = os.path.join(
    current_dir, "..", "..", "Inputs", "Payload_and_Crew_requirements.json"
)
with open(file_path_payload, "r") as file:
    data_payload = js.load(file)
    Npax_value = data_payload["Npax"]
    Baggage_weight_value = data_payload["Baggage_weight"]
    Pax_weight_value = data_payload["Pax_weight"]
    Wpayload_value = Npax_value * (Pax_weight_value + Baggage_weight_value)
    Wcrew_value = data_payload["Wcrew"]


class Aircraft:
    class Design:
        TOW = Variable("TOW", 1, "lbf", description="Takeoff weight")
        WING_LOADING = Variable(
            "wing_loading", unit="lbf/ft^2", description="Wing loading of the aircraft"
        )
        THRUST_TO_WEIGHT = Variable(
            "thrust_to_weight", unit="", description="Thrust to weight ratio"
        )
        Wing_Area = Variable("Wing_Area", 1, "ft^2", description="Wing Area")
        Weight_fractions = Variable(
            "Weight_fractions",
            value=[],
            unit="",
            description="Weight fractions list of the aircraft",
        )
        Sea_level_Thrust = Variable(
            "Sea_level_Thrust", 1, "lbf", description="Sea level thrust of the engine"
        )
        Fuel_Weight = Variable(
            "Fuel_Weight", 1, "lbf", description="Weight of the fuel"
        )

    class Payload:
        Npax = Variable(
            "Npax",
            value=Npax_value,
            unit="",
            description="Number of passengers",
        )
        Baggage_weight = Variable(
            "Baggage_weight",
            value=Baggage_weight_value,
            unit="lbf",
            description="Weight of the baggage",
        )
        Pax_weight = Variable(
            "Pax_weight",
            value=Pax_weight_value,
            unit="lbf",
            description="Weight of the passenger",
        )
        Wcrew = Variable(
            "Wcrew",
            value=Wcrew_value,
            unit="lbf",
            description="Weight of the crew",
        )
        Wpayload = Variable(
            "Wpayload",
            value=Wpayload_value,
            unit="lbf",
            description="Weight of the payload",
        )

    class Structure:
        KWE = Variable(
            "KWE",
            value=K_we_value,
            unit="",
            description="Weight fraction factor for the empty weight",
        )
        Empty_Weight = Variable(
            "Empty weight",
            value=1,
            unit="lbf",
            description="Empty weight of the aircraft",
        )

    class Aerodynamics:
        K1 = Variable(
            "K1",
            value=K_1,
            unit="",
            description="Induced drag factor (square of lift coefficient)",
        )
        K2 = Variable("K2", value=K_2, unit="", description="Induced drag factor")

    class Propulsion:
        ktsfc = Variable(
            "ktsfc",
            value=ktsfc_value,
            unit="",
            description="kTSFC is a technology factor for fuel flow applied on Mattingly’s equation",
        )
