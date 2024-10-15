import numpy as np
import Sizing.MissionProfile.segments as sg
import plotly.graph_objects as go
from typing import List
from Sizing.Variable_info.variables import Aircraft

import os


def weight_breakdown():
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
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=list(weight_dict.keys()),
            y=list(weight_dict.values()),
            marker=dict(color=["blue", "green", "red", "purple", "orange"]),
        )
    )
    fig.update_layout(
        title="Weight Breakdown",
        xaxis_title="Weight Components",
        yaxis_title="Weight (lbs)",
        xaxis=dict(tickmode="array", tickvals=list(weight_dict.keys())),
        yaxis=dict(tickformat=","),
    )
    if not os.path.exists("images"):
        os.mkdir("images")
    fig.write_html("outputs/weight_breakdown.html")
    fig.show()
    return fig


def histo_weights(segment_list: List[sg.segments]):
    Betas_list = Aircraft.Design.Weight_fractions.value
    weights = [
        Betas_list[i] * Aircraft.Design.TOW.value for i in range(len(Betas_list))
    ]
    phases = [str(segment.phase_number) for segment in segment_list]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=phases,
            y=weights,
            marker=dict(color="purple"),
        )
    )
    fig.update_layout(
        title="Weight per Phase",
        xaxis_title="Flight Phases",
        yaxis_title="Weight (lbs)",
        xaxis=dict(tickmode="array", tickvals=phases),
        yaxis=dict(tickformat=","),
    )
    fig.show()
    if not os.path.exists("images"):
        os.mkdir("images")
    fig.write_html("outputs/weight_per_phase.html")
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
