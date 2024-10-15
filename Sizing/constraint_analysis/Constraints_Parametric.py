import Sizing.MissionProfile.Segments.Takeoff as takeoff_segment
import Sizing.MissionProfile.Segments.approach as approach_segment
import Sizing.MissionProfile.Segments.landing as landing_segment
import numpy as np
import matplotlib.pyplot as plt

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
    print("len(segment_list)", len(segment_list))
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

    Additional_Constraints.Additional_constraints(
        names, Thrusts_Weight_ratios, wing_loading
    )  ## Add additional constraints
    wing_loading_landing = float(landing_segment.landing_constraint())

    """
    ADDITIONAL CONSTRAINTS SPECIFIC TO THE PROJECT"""
    ### Additional constraints ###

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

    print(
        f"Design Point: Wing Loading = {wing_loading_design} lb/ft^2, TWR = {TWR_design}"
    )

    """Plotting"""
    fig = go.Figure()
    for i, TWR in enumerate(Thrusts_Weight_ratios):
        fig.add_trace(
            go.Scatter(
                x=wing_loading,
                y=TWR,
                mode="lines",
                name=names[i],
                line=dict(dash="dash" if i < 7 else "solid"),
            )
        )

    fig.add_trace(
        go.Scatter(
            x=wing_loading,
            y=y_max,
            mode="lines",
            name="feasible design space",
            line=dict(color="green", width=4),
        )
    )

    # Remplir l'espace faisable au-dessus de l'enveloppe
    fig.add_trace(
        go.Scatter(
            x=np.concatenate([wing_loading, wing_loading[::-1]]),
            y=np.concatenate([y_max, np.ones_like(y_max)]),  # Remplir jusqu'à y=1
            fill="toself",
            fillcolor="rgba(144, 238, 144, 0.5)",  # Couleur vert clair avec transparence
            line=dict(color="rgba(255,255,255,0)"),
            showlegend=False,
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[wing_loading_landing] * 2,
            y=[0, max(fig.data[-1].y) * 1.1],
            mode="lines",
            name="Landing Constraint",
            line=dict(dash="dash", color="red"),
        )
    )

    fig.update_layout(
        title="Thrust to Weight Ratio vs Wing Loading",
        xaxis_title="Wing Loading (lb/ft^2)",
        yaxis_title="Thrust to Weight Ratio",
        legend_title="Mission Segments",
    )
    if plot:
        fig.show()
    return wing_loading_design, TWR_design
