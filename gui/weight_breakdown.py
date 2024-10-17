import numpy as np
import Sizing.MissionProfile.segments as sg
import plotly.graph_objects as go
from typing import List
from Sizing.Variable_info.variables import Aircraft

import os


def combined_weight_plot(segment_list: List[sg.segments]):
    """
    Generates a combined plot with a dropdown menu to switch between weight breakdown and weight per phase.
    Args:
        segment_list (List[sg.segments]): A list of flight segments, where each segment contains a phase number.
    Returns:
        plotly.graph_objs._figure.Figure: The generated figure with dropdown menu.
    """

    # Data for weight breakdown
    Wcrew = Aircraft.Payload.Wcrew.value
    Wpayload = Aircraft.Payload.Wpayload.value
    Wempty = Aircraft.Structure.Empty_Weight.value
    Wfuel = Aircraft.Design.Fuel_Weight.value
    WTO = Aircraft.Design.TOW.value
    weight_dict = {
        "TOW": WTO,
        "Empty": Wempty,
        "Fuel Weight": Wfuel,
        "Payload": Wpayload,
        "Wcrew": Wcrew,
    }

    # Data for weight per phase
    Betas_list = Aircraft.Design.Weight_fractions.value
    weights = [
        Betas_list[i] * Aircraft.Design.TOW.value for i in range(len(Betas_list))
    ]
    names = [str(segment.name) for segment in segment_list]

    fig = go.Figure()

    # Add traces for weight breakdown
    fig.add_trace(
        go.Bar(
            x=list(weight_dict.keys()),
            y=list(weight_dict.values()),
            marker=dict(color=["blue", "green", "red", "purple", "orange"]),
            name="Weight Breakdown",
        )
    )

    # Add traces for weight per phase (line graph)
    fig.add_trace(
        go.Scatter(
            x=names,
            y=weights,
            mode="lines+markers",
            marker=dict(color="purple"),
            name="Weight per Phase",
        )
    )

    # Create a dropdown menu
    dropdown_buttons = [
        {
            "label": "Weight Breakdown",
            "method": "update",
            "args": [
                {"visible": [True, False]},
                {
                    # "title": "Weight Breakdown",
                    "xaxis": {"title": "Weight Categories"},
                    "yaxis": {"title": "Weight (lbs)"},
                },
            ],
        },
        {
            "label": "Weight per Phase",
            "method": "update",
            "args": [
                {"visible": [False, True]},
                {
                    # "title": "Weight per Phase",
                    "xaxis": {"title": "Flight Phases"},
                    "yaxis": {"title": "Weight (lbs)"},
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

    # Set initial visibility
    fig.data[0].visible = True
    fig.data[1].visible = False
    fig.update_layout(
        title="Weight Breakdown and Weight per Phase",
        xaxis_title="Weight Categories",
        yaxis_title="Weight (lbs)",
    )
    if not os.path.exists("outputs"):
        os.mkdir("outputs")
    fig.write_html("outputs/combined_weight_plot.html")
    fig.show()
    return fig


def print_Final_Design():
    print("\n")
    print("############################################")
    print("Final Design")
    print("############################################")
    print(Aircraft.Design.TOW)
    print(Aircraft.Design.WING_LOADING)
    print(Aircraft.Design.THRUST_TO_WEIGHT)
    print(Aircraft.Design.Wing_Area)
    print(Aircraft.Design.Sea_level_Thrust)
    print(Aircraft.Design.Fuel_Weight)
    print(Aircraft.Geometry.Wing.Span)
    print(Aircraft.Geometry.Wing.Aspect_Ratio)
    print("############################################")
    print("############################################")
    print("\n")

    def generate_table():
        with open("outputs/final_design_results.html", "w") as file:
            html_table = f"""
            <h2>Main Results</h2>
            <table>
            <tr>
                <th>Parameter</th>
                <th>Value</th>
                <th>Unit</th>
            </tr>
            <tr>
                <td>TOW</td>
                <td>{Aircraft.Design.TOW.value}</td>
                <td>{Aircraft.Design.TOW.unit}</td>
            </tr>
            <tr>
                <td>Wing Loading</td>
                <td>{Aircraft.Design.WING_LOADING.value}</td>
                <td>{Aircraft.Design.WING_LOADING.unit}</td>
            </tr>
            <tr>
                <td>Thrust to Weight</td>
                <td>{Aircraft.Design.THRUST_TO_WEIGHT.value}</td>
                <td>{Aircraft.Design.THRUST_TO_WEIGHT.unit}</td>
            </tr>
            <tr>
                <td>Wing Area</td>
                <td>{Aircraft.Design.Wing_Area.value}</td>
                <td>{Aircraft.Design.Wing_Area.unit}</td>
            </tr>
            <tr>
                <td>Wing Aspect ratio </td>
                <td>{Aircraft.Geometry.Wing.Aspect_Ratio.unit}</td>
                <td>{Aircraft.Geometry.Wing.Aspect_Ratio.unit}</td>
            </tr>  
            <tr>
                <td>Wing Span</td>
                <td>{Aircraft.Geometry.Wing.Span.value}</td>
                <td>{Aircraft.Geometry.Wing.Span.unit}</td>
            </tr>          
            <tr>
                <td>Sea Level Thrust</td>
                <td>{Aircraft.Design.Sea_level_Thrust.value}</td>
                <td>{Aircraft.Design.Sea_level_Thrust.unit}</td>
            </tr>
            <tr>
                <td>Fuel Weight</td>
                <td>{Aircraft.Design.Fuel_Weight.value}</td>
                <td>{Aircraft.Design.Fuel_Weight.unit}</td>
            </tr>
            </table>
            """
            file.write(html_table)

    generate_table()
