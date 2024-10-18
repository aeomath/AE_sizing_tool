import numpy as np
import Sizing.MissionProfile.segments as sg
import plotly.graph_objects as go
from typing import List
from Sizing.Variable_info.variables import Aircraft

import os


def plots_aero_prop(segment_list: List[sg.segments]):
    """
    Generates a chart representing the lift-to-drag ratios of an aircraft for different flight phases.
    The function retrieves the lift-to-drag ratios for each flight phase and creates
    a chart using Plotly to visualize these ratios. The chart is saved as an HTML file in the "outputs"
    directory and is also displayed in the browser.
    Returns:
        fig (plotly.graph_objs._figure.Figure): The generated Plotly figure object.
    """

    phases = [str(segment.phase_number) for segment in segment_list]
    names = [str(segment.name) for segment in segment_list]
    WSR = Aircraft.Design.WING_LOADING.value
    TSL = Aircraft.Design.Sea_level_Thrust.value
    lift_drag_ratios = [float(segment.lift_drag_ratio(WSR)) for segment in segment_list]
    tsfc = [float(segment.tsfc(WSR)) * 3600 for segment in segment_list]
    lift_coefficients = [float(segment.Cl(WSR)) for segment in segment_list]
    drag_coefficients = [float(segment.Cd(WSR)) for segment in segment_list]
    thruts = [float(segment.alpha_seg(WSR)) * TSL for segment in segment_list]

    fig = go.Figure()

    # Create a dropdown menu
    dropdown_buttons = [
        {
            "label": "Lift-to-Drag Ratios",
            "method": "update",
            "args": [
                {"visible": [True, False, False, False, False]},
                {
                    # "title": "Lift-to-Drag Ratios per Phase",
                    "yaxis": {"title": "Lift-to-Drag Ratio"},
                },
            ],
        },
        {
            "label": "TSFC",
            "method": "update",
            "args": [
                {"visible": [False, True, False, False, False]},
                {"yaxis": {"title": "TSFC"}},
            ],
        },
        {
            "label": "Lift Coefficients",
            "method": "update",
            "args": [
                {"visible": [False, False, True, False, False]},
                {
                    # "title": "Lift Coefficients per Phase",
                    "yaxis": {"title": "Lift Coefficient"},
                },
            ],
        },
        {
            "label": "Drag Coefficients",
            "method": "update",
            "args": [
                {"visible": [False, False, False, True, False]},
                {
                    # "title": "Drag Coefficients per Phase",
                    "yaxis": {"title": "Drag Coefficient"},
                },
            ],
        },
        {
            "label": "Thrust available (full throttle)",
            "method": "update",
            "args": [
                {"visible": [False, False, False, False, True]},
                {
                    # "title": "Thrust per Phase",
                    "yaxis": {"title": "Thrust"},
                },
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

    # Add traces
    fig.add_trace(
        go.Scatter(
            x=names,
            y=lift_drag_ratios,
            mode="lines+markers",
            name="Lift-to-Drag Ratios",
            line=dict(color="blue"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=names,
            y=tsfc,
            mode="lines",
            name="TSFC",
            line=dict(color="red"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=names,
            y=lift_coefficients,
            mode="lines",
            name="Lift Coefficients",
            line=dict(color="green"),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=names,
            y=drag_coefficients,
            mode="lines",
            name="Drag Coefficients",
            line=dict(color="purple"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=names,
            y=thruts,
            mode="lines",
            name="Thrust",
            line=dict(color="orange"),
        )
    )
    # Set initial visibility
    fig.data[0].visible = True
    fig.data[1].visible = False
    fig.data[2].visible = False
    fig.data[3].visible = False
    fig.data[4].visible = False

    # Update layout
    fig.update_layout(
        title="Aerodynamic and Propulsion Characteristics per Phase",
        xaxis_title="Flight Phases",
        yaxis_title="Lift-to-Drag Ratio",
        xaxis=dict(tickmode="array", tickvals=names),
    )

    if not os.path.exists("outputs"):
        os.mkdir("outputs")
    fig.write_html("outputs/aero_and_prop_characteristics.html")
    fig.show()
    return fig
