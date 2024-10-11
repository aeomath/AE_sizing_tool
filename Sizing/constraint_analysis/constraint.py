import Sizing.MissionProfile.Segments as Mission_segments
import Sizing.utils.Constants as const
import Sizing.MissionProfile.Segments.acceleration as acceleration_segment
import Sizing.MissionProfile.Segments.Cruise as cruise_segment
import Sizing.MissionProfile.Segments.Climb as climb_segment
import Sizing.MissionProfile.Segments.Takeoff as takeoff_segment
import Sizing.MissionProfile.Segments.approach as approach_segment
import Sizing.MissionProfile.Segments.landing as landing_segment
import numpy as np
import matplotlib.pyplot as plt

import Sizing.utils.utils as utils

import plotly.graph_objects as go


def constraint_analysis_main(plot=False):
    wing_min = 30
    wing_max = 170
    num_points = 700
    wing_loading = np.linspace(wing_min, wing_max, num_points)

    thrust_to_weight_ratios = []
    fig = go.Figure()

    ### Phase 2 ###
    Take_off = takeoff_segment.Takeoff(5500, 0.96, 35)
    TWR_takeoff = Take_off.Thrust_weight_ratio(wing_loading)
    thrust_to_weight_ratios.append(TWR_takeoff)

    ### Phase 3 ###
    first_climb = climb_segment.climb(
        climb_rate=3000,
        KEAS=250,
        start_altitude=0,
        end_altitude=10000,
        time=100,
        weight_fraction=0.7,
    )
    TWR_first_climb = first_climb.Thrust_to_weight_ratio(wing_loading)
    thrust_to_weight_ratios.append(TWR_first_climb)

    ### Phase 4 ###
    acceleration1 = acceleration_segment.acceleration(
        KEAS_start=250, KEAS_end=290, time=60, weight_fraction=0.8, altitude=10000
    )
    TWR_acceleration = acceleration1.Thrust_Weight_Ratio(wing_loading)
    thrust_to_weight_ratios.append(TWR_acceleration)

    ### Phase 5 ###
    Goal_Mach = 0.78
    crossover_alt = utils.crossover_altitude(Goal_Mach, 290)
    climb_to_crossover = climb_segment.climb(
        climb_rate=3000,
        start_altitude=10000,
        end_altitude=crossover_alt,
        weight_fraction=0.8,
        time=100,
        KEAS=290,
        MACH=None,
    )
    TWR_climb_to_crossover = climb_to_crossover.Thrust_to_weight_ratio(wing_loading)
    thrust_to_weight_ratios.append(TWR_climb_to_crossover)

    ### Phase 6 ###

    climb_to_cruise = climb_segment.climb(
        climb_rate=1500,
        start_altitude=crossover_alt,
        end_altitude=35000,
        time=100,
        weight_fraction=0.75,
        KEAS=None,
        MACH=0.78,
    )
    TWR_climb_to_cruise = climb_to_cruise.Thrust_to_weight_ratio(wing_loading)
    thrust_to_weight_ratios.append(TWR_climb_to_cruise)

    ### Phase 7 ###

    cruise1 = cruise_segment.cruise(
        altitude=35000, range=500, weight_fraction=0.6, Mach=0.78
    )
    TWR_cruise = cruise1.Thrust_weight_ratio(wing_loading)
    thrust_to_weight_ratios.append(TWR_cruise)

    ### Phase 8 ###

    descent = climb_segment.climb(
        climb_rate=-1500,
        start_altitude=35000,
        end_altitude=3000,
        time=100,
        weight_fraction=0.6,
        KEAS=250,
        MACH=None,
    )
    TWR_descent = descent.Thrust_to_weight_ratio(wing_loading)
    thrust_to_weight_ratios.append(TWR_descent)

    ### Phase 9 ###
    TWR_deceleration = 0 * wing_loading
    thrust_to_weight_ratios.append(TWR_deceleration)

    ### Phase 10 ###
    approach = approach_segment.approach(
        flight_path_angle=3,
        KEAS=250,
        start_altitude=3000,
        end_altitude=0,
        weight_fraction=0.85,
    )
    TWR_approach = approach.thrust_weight_ratio(wing_loading)
    thrust_to_weight_ratios.append(TWR_approach)

    ### Phase 11 ###
    Take_off_go_around = takeoff_segment.Takeoff(
        takeoff_distance=5500,
        weight_fraction=0.6,
        obstacle_height=0,
        mu=0.05,
        Cd_r=0.07,
        Cl_max=2.56,
        kt0=1.2,
        altitude_runway=0,
        tr=3,
    )
    TWR_go_around = Take_off_go_around.Thrust_weight_ratio(wing_loading)
    thrust_to_weight_ratios.append(TWR_go_around)

    ### Phase 12 ###
    cruise_reserve = cruise_segment.cruise(
        altitude=15000, range=200, weight_fraction=0.6, EAS=250
    )
    TWR_cruise_reserve = cruise_reserve.Thrust_weight_ratio(wing_loading)
    thrust_to_weight_ratios.append(TWR_cruise_reserve)

    ### Phase 13 ###
    print("Loiter")
    loiter = cruise_segment.cruise(
        altitude=15000,
        range=200,
        weight_fraction=0.6,
        EAS=250,
    )
    TWR_loiter = loiter.Thrust_weight_ratio(wing_loading)
    thrust_to_weight_ratios.append(TWR_loiter)

    ### Additional constraints ###
    ### Service Ceiling ###

    service_ceiling = 41000
    Mach = 0.78
    ceiling = climb_segment.climb(
        climb_rate=100,
        start_altitude=service_ceiling,
        end_altitude=service_ceiling,
        time=100,
        weight_fraction=0.75,
        KEAS=None,
        MACH=Mach,
    )
    TWR_service_ceiling = ceiling.Thrust_to_weight_ratio(wing_loading)
    thrust_to_weight_ratios.append(TWR_service_ceiling)

    ### Maximum Mach Number ###
    max_Mach = 0.82
    maximum_mach_segment = cruise_segment.cruise(
        altitude=35000,
        range=500,
        weight_fraction=0.75,
        Mach=max_Mach,
    )
    TWR_max_mach = maximum_mach_segment.Thrust_weight_ratio(wing_loading)
    thrust_to_weight_ratios.append(TWR_max_mach)

    ### Steep Turn ###
    turn_segment = cruise_segment.cruise(
        altitude=35000, range=500, weight_fraction=0.75, Mach=0.78, bank_angle=45
    )
    TWR_steep_turn = turn_segment.Thrust_weight_ratio(wing_loading)
    thrust_to_weight_ratios.append(TWR_steep_turn)

    ### Climb with one engine ###
    takeoff_one_engine = takeoff_segment.Takeoff(5500, 1, kt0=1.3)
    print("Climb with one engine")
    gradient_percent = 0.05
    path_angle = np.arctan(gradient_percent) * 180 / np.pi
    takeoff_speed = takeoff_one_engine.takeoff_EAS_speed(wing_loading)
    climb_one_engine_segment = climb_segment.climb(
        KEAS=takeoff_speed,
        start_altitude=0,
        end_altitude=5000,
        time=100,
        weight_fraction=1,
        flight_path_angle=path_angle,
    )
    # takeoff_speed = 160
    TWR_climb_one_engine = 2 * climb_one_engine_segment.Thrust_to_weight_ratio(
        wing_loading
    )
    thrust_to_weight_ratios.append(TWR_climb_one_engine)
    phase_names = [
        "Takeoff",
        "First Climb",
        "Acceleration",
        "Climb to Crossover",
        "Climb to Cruise",
        "Cruise",
        "Descent",
        "Deceleration",
        "Approach",
        "Go Around",
        "Cruise Reserve",
        "Loiter",
        "Service Ceiling",
        "Maximum Mach Number",
        "Steep Turn",
        "Climb with One Engine",
    ]
    ### Landing constraint ###
    landing = landing_segment.landing(
        weight_fraction=0.85, KEAS=135, Cl_max=3, k_land=1.3
    )
    wing_loading_landing = float(landing.landing_constraint())

    """Find the feasible design space and Design Point"""
    ## Find the feasibke design space
    y_max = np.max(thrust_to_weight_ratios, axis=0)
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

    """PLOTS"""
    for i, TWR in enumerate(thrust_to_weight_ratios):
        fig.add_trace(
            go.Scatter(
                x=wing_loading,
                y=TWR,
                mode="lines",
                name=phase_names[i],
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
