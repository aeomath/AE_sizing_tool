"""
Main.py
This script is the main entry point for the AE Sizing Tool project. It performs the following tasks:
1. Loads input data for payload and crew requirements from a JSON file.
2. Loads the mission profile from a JSON file.
3. Runs the main sizing loop to calculate the final aircraft parameters.
4. Displays the results using a graphical user interface.
Modules:
- Data_formating: Contains functions to load and format input data.
- Beta_loop: Contains the main loop for aircraft sizing calculations.
- gui: Contains functions for displaying results.
Functions:
- load_payload_and_crew_requirements: Loads payload and crew requirements from a JSON file.
- load_mission_profile: Loads the mission profile from a JSON file.
- main_loop: Runs the main sizing loop to calculate aircraft parameters.
- weight_breakdown: Displays a breakdown of the aircraft weight.
- histo_weights: Displays a histogram of the aircraft weights.
"""

import argparse as argparse
import os
import Data_formating as df
import Beta_loop as bl
import gui as gui
from Sizing.Variable_info.variables import Aircraft
import gui.Constraints_plot
import gui.aero_prop
import gui.weight_breakdown


def main(mission_file):
    print("\n")
    print("#############################################")
    print("Begining Design Process... (This may take a few minutes)")
    print("#############################################")
    print("\n")
    # Find the Inputs and requirements from the Inputs folder
    current_dir = os.path.dirname(__file__)
    Inputs_dir = os.path.join(current_dir, "Inputs")
    Inputs_dir = os.path.normpath(Inputs_dir)

    # Load the mission profile from the specified mission file
    mission_data = df.load_mission_profile(os.path.join(Inputs_dir, mission_file))

    # Run the case
    results = bl.main_loop(
        Mission=mission_data,
        WC=Aircraft.Payload.Wcrew.value,
        WP=Aircraft.Payload.Wpayload.value,
        guess_WTO=10000,
        max_iteration=20,
        tolerance=0.001,
        WSR_guess=110,
        TWR_guess=0.3,
    )

    WTO = results[0]
    WSR = results[1]
    TWR = results[2]
    Beta_final = results[3]
    Beta_list = results[4]
    constraints = results[5]
    print(Beta_list)

    wing_loading_range = constraints[2]
    thrust_weight_lists = constraints[3]
    ymax_constraints = constraints[4]
    wing_loading_landing = constraints[5]
    names_constraints = constraints[6]

    # Adding the final values to the Aircraft class
    Aircraft.Design.TOW.value = WTO
    Aircraft.Design.WING_LOADING.value = WSR
    Aircraft.Design.THRUST_TO_WEIGHT.value = TWR
    Aircraft.Design.Weight_fractions.value = Beta_list
    Aircraft.Design.Wing_Area.value = WTO / WSR
    Aircraft.Design.Sea_level_Thrust.value = TWR * WTO
    Aircraft.Geometry.Wing.Span.value = (
        Aircraft.Geometry.Wing.Aspect_Ratio.value * Aircraft.Design.Wing_Area.value
    ) ** 0.5

    # Calculate the empty weight and fuel weight
    def empty_weight(WTO):
        kwe = 1.15
        return WTO * kwe / (WTO**0.06)

    def fuel_weight(WTO, beta_final):
        ### 1.06 is obtained from empirical data
        return 1.06 * (1 - beta_final) * WTO

    Aircraft.Structure.Empty_Weight.value = empty_weight(WTO)
    Aircraft.Design.Fuel_Weight.value = fuel_weight(WTO, Beta_final)

    # Display the results using the GUI
    gui.aero_prop.plots_aero_prop(mission_data)
    gui.weight_breakdown.combined_weight_plot(mission_data)
    gui.Constraints_plot.T_WS_WS_diagram(mission_data)
    gui.weight_breakdown.print_Final_Design()
    gui.Constraints_plot.constraints_plots(
        wing_loading=wing_loading_range,
        Thrusts_Weight_ratios=thrust_weight_lists,
        y_max=ymax_constraints,
        wing_loading_landing=wing_loading_landing,
        names=names_constraints,
    )
    print("Aircraft Design Completed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aircraft Design Tool")
    parser.add_argument(
        "mission_file",
        type=str,
        nargs="?",
        help="Mission file to load",
        default="Mission_Profile.json",
    )
    args = parser.parse_args()
    main(args.mission_file)
