import os
from typing import List
import plotly.graph_objects as go
import Sizing.MissionProfile.segments as sg
from Sizing.Variable_info.variables import Aircraft
import numpy as np


def T_WS_WS_diagram(segment_list: List[sg.segments]):
    """
    Generates and displays bar plots for Thrust-to-Weight Ratio (TWR) and Wing Loading (WSR)
    for each flight phase based on the provided segment list. The plots are saved as HTML files.
    Parameters:
    segment_list (List[sg.segments]): A list of flight segments, where each segment contains
                                      information about the flight phase and alpha segment.
    Returns:
    None
    The function performs the following steps:
    1. Retrieves weight fractions, thrust-to-weight ratio, and wing loading from the Aircraft design.
    2. Extracts phase numbers and calculates alpha values for each segment.
    3. Asserts that the number of alphas matches the number of weight fractions.
    4. Calculates TWR and WSR for each phase.
    5. Creates and displays a bar plot for TWR per phase.
    6. Saves the TWR plot as an HTML file in the "outputs" directory.
    7. Creates and displays a bar plot for WSR per phase.
    8. Saves the WSR plot as an HTML file in the "outputs" directory.
    """

    Betas_list = Aircraft.Design.Weight_fractions.value
    TWR_to = Aircraft.Design.THRUST_TO_WEIGHT.value
    WSR_to = Aircraft.Design.WING_LOADING.value
    phases = [str(segment.phase_number) for segment in segment_list]
    names = [str(segment.name) for segment in segment_list]
    alphas = [segment.alpha_seg(WSR_to) for segment in segment_list]
    ## Check if the number of alphas is the same as the number of segments
    assert len(alphas) == len(Betas_list)
    TWR = [float(alphas[i]) / Betas_list[i] * TWR_to for i in range(len(Betas_list))]
    WSR = [float(alphas[i]) / Betas_list[i] * WSR_to for i in range(len(Betas_list))]
    fig = go.Figure()

    # Add traces for TWR and WSR
    fig.add_trace(
        go.Bar(
            x=names,
            y=TWR,
            marker=dict(color="blue"),
            name="Thrust-to-Weight Ratio",
        )
    )
    fig.add_trace(
        go.Bar(
            x=names,
            y=WSR,
            marker=dict(color="green"),
            name="Wing Loading",
        )
    )

    # Create a dropdown menu
    dropdown_buttons = [
        {
            "label": "Thrust-to-Weight Ratio",
            "method": "update",
            "args": [
                {"visible": [True, False]},
                {
                    "title": "Thrust-to-Weight Ratio per Phase",
                    "yaxis": {"title": "TWR"},
                },
            ],
        },
        {
            "label": "Wing Loading",
            "method": "update",
            "args": [
                {"visible": [False, True]},
                {"title": "Wing Loading per Phase", "yaxis": {"title": "WSR"}},
            ],
        },
    ]

    # Add dropdown menu to the layout
    fig.update_layout(
        updatemenus=[
            {
                "buttons": dropdown_buttons,
                "direction": "down",
                "showactive": True,
            }
        ]
    )

    # Set initial visibility
    fig.data[0].visible = True
    fig.data[1].visible = False

    # Update layout
    fig.update_layout(
        title="Thrust-to-Weight Ratio per Phase",
        xaxis_title="Flight Phases",
        yaxis_title="TWR",
        xaxis=dict(tickmode="array", tickvals=phases),
        yaxis=dict(tickformat=",.2f"),
    )

    if not os.path.exists("outputs"):
        os.mkdir("outputs")
    fig.write_html("outputs/TWR_WSR_per_phase.html")
    fig.show()
    return fig


def constraints_plots(
    wing_loading,
    Thrusts_Weight_ratios,
    y_max,
    wing_loading_landing,
    names,
):

    final_TWR = Aircraft.Design.THRUST_TO_WEIGHT.value
    final_WSR = Aircraft.Design.WING_LOADING.value
    """Plotting"""
    fig = go.Figure()
    for i, TWR in enumerate(Thrusts_Weight_ratios):
        fig.add_trace(
            go.Scatter(
                x=wing_loading,
                y=TWR,
                mode="lines",
                name=names[i],
                line=dict(dash="dash" if i < 10 else "solid"),
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

    # Add a red point for the final WSR and TWR
    fig.add_trace(
        go.Scatter(
            x=[final_WSR],
            y=[final_TWR],
            mode="markers",
            name="Final Design Point",
            marker=dict(color="red", size=10, symbol="circle"),
        )
    )

    # Fill the feasible design space
    fig.add_trace(
        go.Scatter(
            x=np.concatenate([wing_loading, wing_loading[::-1]]),
            y=np.concatenate(
                [y_max, np.ones_like(y_max)]
            ),  # fill to the top of the plot
            fill="toself",
            fillcolor="rgba(144, 238, 144, 0.5)",  # Light Green
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
    if not os.path.exists("outputs"):
        os.mkdir("outputs")
    fig.write_html("outputs/TWR_vs_Wing_Loading.html")
    # fig.write_image("outputs/TWR_vs_Wing_Loading.png")
    fig.show()
