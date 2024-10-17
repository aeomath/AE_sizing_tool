import Sizing.MissionProfile.Segments.Takeoff as takeoff_segment
import Sizing.MissionProfile.Segments.approach as approach_segment
import Sizing.MissionProfile.Segments.landing as landing_segment
import numpy as np
import matplotlib.pyplot as plt
import os


import Sizing.utils.utils as utils
import Sizing.constraint_analysis.Additional_Constraints as Additional_Constraints
import plotly.graph_objects as go
from Sizing.MissionProfile.segments import segments
from typing import List


def constraint_analysis_main(segment_list: List[segments], plot=False):
    wing_min = 30
    wing_max = 170
    num_points = 700
    wing_loading = np.linspace(wing_min, wing_max, num_points)
    Thrusts_Weight_ratios = []
    names = []
    # print("len(segment_list)", len(segment_list))
    for i in range(len(segment_list)):
        names.append(segment_list[i].name)
        # print(
        #     f"Computing {segment_list[i].name} segment",
        #     "Phase number: ",
        #     segment_list[i].phase_number,
        # )
        # print(segment_list[i].weight_fraction)
        Thrusts_Weight_ratios.append(segment_list[i].Thrust_Weight_Ratio(wing_loading))
        if segment_list[i].type == "Landing":
            landing_segment = segment_list[i]  ## Save the landing segment for later
        ## Test if the sement is top of climb
        if segment_list[i].phase_number == 6:
            weight_fraction_top_of_climb = segment_list[i].weight_fraction.value

    """ADDITIONAL CONSTRAINTS SPECIFIC TO THE PROJECT"""
    ### Additional constraints ###

    Additional_Constraints.Additional_constraints(
        names, Thrusts_Weight_ratios, wing_loading, weight_fraction_top_of_climb
    )
    """END OF ADDITIONAL CONSTRAINTS"""

    """Find the landing constraint"""
    wing_loading_landing = float(landing_segment.landing_constraint())
    """END OF LANDING CONSTRAINT"""

    """Find the feasible design space and Design Point"""
    y_max = np.max(Thrusts_Weight_ratios, axis=0)
    # Find the index of the minimum in the envelope curve
    min_index = np.argmin(y_max)
    # Retrieve the corresponding x and y values for the minimum point
    wing_loading_design = wing_loading[min_index]
    TWR_design = y_max[min_index]

    # If the landing constraint is more restrictive than the design point, update the design point
    if wing_loading_design > wing_loading_landing:
        wing_loading_design = wing_loading_landing
        # Find the index of the wing_loading_landing in the wing_loading array
        landing_index = np.where(
            np.abs(wing_loading - wing_loading_landing)
            <= (wing_max - wing_min) / num_points
        )[0][0]
        TWR_design = float(y_max[landing_index])
        print("Landing constraint is more restrictive than the design point")

    # print(
    #     f"Design Point: Wing Loading = {wing_loading_design} lb/ft^2, TWR = {TWR_design}"
    # )
    return (
        wing_loading_design,
        TWR_design,
        wing_loading,
        Thrusts_Weight_ratios,
        y_max,
        wing_loading_landing,
        names,
    )
