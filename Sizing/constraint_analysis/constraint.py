from Sizing.MissionProfile.Segments import Mission_segments
import Sizing.utils.Constants as const
from Sizing.constraint_analysis import (
    climb,
    acceleration,
    takeoff,
    cruise,
    approach_landing,
)
import numpy as np
import matplotlib.pyplot as plt


import plotly.graph_objects as go


def constraint_analysis_plot():
    wing_loading = np.linspace(30, 170, 700)
    styles = [
        "solid",
        "dash",
        "dot",
        "dashdot",
        "solid",
        "dash",
        "dot",
        "dashdot",
        "solid",
        "dash",
        "dot",
        "dashdot",
        "solid",
        "dash",
        "dot",
    ]
    colors = [
        "blue",
        "green",
        "red",
        "cyan",
        "magenta",
        "yellow",
        "black",
        "orange",
        "purple",
        "brown",
        "pink",
        "gray",
        "olive",
        "cyan",
        "lime",
    ]

    fig = go.Figure()

    ### Phase 2 ###
    Take_off = Mission_segments.Takeoff(5500, 0.96, 35)
    fig.add_trace(
        go.Scatter(
            x=wing_loading,
            y=takeoff.Thrust_weight_ratio(
                wing_loading,
                Take_off.weight_fraction.value,
                2.56,
                Take_off.takeoff_distance.value,
                hobst=Take_off.obstacle_height.value,
            ),
            mode="lines",
            name="Takeoff",
            line=dict(dash=styles[0], color=colors[0]),
        )
    )

    ### Phase 3 ###
    first_climb = Mission_segments.climb(
        climb_rate=3000,
        KEAS=250,
        start_altitude=0,
        end_altitude=10000,
        time=100,
        weight_fraction=0.7,
    )
    fig.add_trace(
        go.Scatter(
            x=wing_loading,
            y=climb.Thrust_to_weight_ratio_2(
                wing_loading=wing_loading, mission_segment=first_climb
            ),
            mode="lines",
            name="First Climb",
            line=dict(dash=styles[1], color=colors[1]),
        )
    )

    ### Phase 4 ###
    acceleration1 = Mission_segments.acceleration(
        KEAS_start=250, KEAS_end=290, time=60, weight_fraction=0.8, altitude=10000
    )
    fig.add_trace(
        go.Scatter(
            x=wing_loading,
            y=acceleration.Thrust_Weight_Ratio(wing_loading, acceleration1),
            mode="lines",
            name="Acceleration",
            line=dict(dash=styles[2], color=colors[2]),
        )
    )

    ### Phase 5 ###
    Goal_Mach = 0.78
    crossover_alt = climb.crossover_altitude(Goal_Mach, 290)
    climb_to_crossover = Mission_segments.climb(
        climb_rate=3000,
        start_altitude=10000,
        end_altitude=crossover_alt,
        weight_fraction=0.8,
        time=100,
        KEAS=290,
        MACH=None,
    )
    fig.add_trace(
        go.Scatter(
            x=wing_loading,
            y=climb.Thrust_to_weight_ratio_2(wing_loading, climb_to_crossover),
            mode="lines",
            name="Climb to Crossover",
            line=dict(dash=styles[3], color=colors[3]),
        )
    )

    ### Phase 6 ###
    climb_to_cruise = Mission_segments.climb(
        climb_rate=1500,
        start_altitude=crossover_alt,
        end_altitude=35000,
        time=100,
        weight_fraction=0.75,
        KEAS=None,
        MACH=0.78,
    )
    fig.add_trace(
        go.Scatter(
            x=wing_loading,
            y=climb.Thrust_to_weight_ratio_2(wing_loading, climb_to_cruise),
            mode="lines",
            name="Climb to Cruise",
            line=dict(dash=styles[4], color=colors[4]),
        )
    )

    ### Phase 7 ###
    cruise1 = Mission_segments.cruise(
        altitude=35000, range=500, weight_fraction=0.6, Mach=0.78
    )
    fig.add_trace(
        go.Scatter(
            x=wing_loading,
            y=cruise.Thrust_weight_ratio(wing_loading, cruise1),
            mode="lines",
            name="Cruise",
            line=dict(dash=styles[5], color=colors[5]),
        )
    )

    ### Phase 8 ###
    descent = Mission_segments.climb(
        climb_rate=-1500,
        start_altitude=35000,
        end_altitude=3000,
        time=100,
        weight_fraction=0.6,
        KEAS=250,
        MACH=None,
    )
    fig.add_trace(
        go.Scatter(
            x=wing_loading,
            y=climb.Thrust_to_weight_ratio_2(wing_loading, descent),
            mode="lines",
            name="Descent1",
            line=dict(dash=styles[6], color=colors[6]),
        )
    )

    ### Phase 9 ###
    fig.add_trace(
        go.Scatter(
            x=wing_loading,
            y=0 * wing_loading,
            mode="lines",
            name="Deceleration",
            line=dict(dash=styles[7], color=colors[7]),
        )
    )

    ### Phase 10 ###
    approach = Mission_segments.approach(
        flight_path_angle=3,
        KEAS=250,
        start_altitude=3000,
        end_altitude=0,
        weight_fraction=0.85,
    )
    fig.add_trace(
        go.Scatter(
            x=wing_loading,
            y=approach_landing.thrust_weight_ratio_approach(wing_loading, approach),
            mode="lines",
            name="Approach",
            line=dict(dash=styles[8], color=colors[8]),
        )
    )

    ### Phase 11 ###
    Take_off = Mission_segments.Takeoff(5500, 0.6, 0)
    fig.add_trace(
        go.Scatter(
            x=wing_loading,
            y=takeoff.Thrust_weight_ratio(
                wing_loading,
                Take_off.weight_fraction.value,
                2.56,
                Take_off.takeoff_distance.value,
                hobst=Take_off.obstacle_height.value,
            ),
            mode="lines",
            name="Go Around",
            line=dict(dash=styles[9], color=colors[9]),
        )
    )

    ### Phase 12 ###
    cruise_reserve = Mission_segments.cruise(
        altitude=15000, range=200, weight_fraction=0.6, EAS=250
    )
    fig.add_trace(
        go.Scatter(
            x=wing_loading,
            y=cruise.Thrust_weight_ratio(wing_loading, cruise_reserve),
            mode="lines",
            name="Cruise Reserve",
            line=dict(dash=styles[10], color=colors[10]),
        )
    )

    ### Phase 13 ###
    loiter = Mission_segments.cruise(
        altitude=15000,
        range=200,
        weight_fraction=0.6,
        EAS=250,
    )
    T_W_loiter = cruise.Thrust_weight_ratio(
        wing_loading, loiter, Equi_Speed=cruise.iter_best_L_D_speed(15000, wing_loading)
    )
    fig.add_trace(
        go.Scatter(
            x=wing_loading,
            y=T_W_loiter,
            mode="lines",
            name="Loiter",
            line=dict(dash=styles[11], color=colors[11]),
        )
    )

    ### Additional constraints ###
    ### Service Ceiling ###
    service_ceiling = 41000
    Mach = 0.78
    ceiling = Mission_segments.climb(
        climb_rate=100,
        start_altitude=service_ceiling,
        end_altitude=service_ceiling,
        time=100,
        weight_fraction=0.75,
        KEAS=None,
        MACH=Mach,
    )
    fig.add_trace(
        go.Scatter(
            x=wing_loading,
            y=climb.Thrust_to_weight_ratio_2(wing_loading, ceiling),
            mode="lines",
            name="Service Ceiling",
            line=dict(dash=styles[12], color=colors[12]),
        )
    )

    ### Maximum Mach Number ###
    max_Mach = 0.82
    maximum_mach_segment = Mission_segments.cruise(
        altitude=35000,
        range=500,
        weight_fraction=0.75,
        Mach=max_Mach,
    )
    fig.add_trace(
        go.Scatter(
            x=wing_loading,
            y=cruise.Thrust_weight_ratio(wing_loading, maximum_mach_segment),
            mode="lines",
            name="Max Mach",
            line=dict(dash=styles[13], color=colors[13]),
        )
    )

    ### Steep Turn ###
    turn_segment = Mission_segments.cruise(
        altitude=35000, range=500, weight_fraction=0.75, Mach=0.78, bank_angle=45
    )
    fig.add_trace(
        go.Scatter(
            x=wing_loading,
            y=cruise.Thrust_weight_ratio(wing_loading, turn_segment),
            mode="lines",
            name="45 deg Turn",
            line=dict(dash=styles[14], color=colors[14]),
        )
    )

    ### Landing  constraint ###
    landing = Mission_segments.landing(KEAS=135, weight_fraction=0.85, Cl_max=3)
    wing_loading_landing = float(approach_landing.landing_constraint(landing))
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

    fig.show()
