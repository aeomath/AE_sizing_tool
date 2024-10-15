import numpy as np
import Sizing.MissionProfile.segments as sg
import plotly.graph_objects as go
from typing import List
from Sizing.Variable_info.variables import Aircraft
from Sizing.Variable_info.Variable import Variable
import tkinter as tk
from tkinter import ttk


def weight_breakdown():
    Wcrew = Aircraft.Payload.Wcrew.value
    Wpayload = Aircraft.Payload.Wpayload.value
    Wempty = Aircraft.Structure.Empty_Weight.value
    Wfuel = Aircraft.Design.Fuel_Weight.value
    weight_dict = {
        "Payload": Wpayload,
        "Wcrew": Wcrew,
        "Empty": Wempty,
        "Fuel Weight": Wfuel,
    }
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=list(weight_dict.keys()),
            y=list(weight_dict.values()),
            marker=dict(color=["blue", "green", "red", "yellow"]),
        )
    )
    fig.update_layout(
        title="Weight Breakdown",
        xaxis_title="Weight Components",
        yaxis_title="Weight (lbs)",
        xaxis=dict(tickmode="array", tickvals=list(weight_dict.keys())),
        yaxis=dict(tickformat=","),
    )
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
    return fig


def print_Final_Design():
    print("############################################")
    print("Final Design")
    print("############################################")
    print(Aircraft.Design.TOW)
    print(Aircraft.Design.WING_LOADING)
    print(Aircraft.Design.THRUST_TO_WEIGHT)
