import numpy as np
import tkinter as tk
from tkinter import ttk
import Sizing.MissionProfile.Segments.acceleration as acceleration_segment
import Sizing.MissionProfile.Segments.Cruise as cruise_segment
import Sizing.MissionProfile.Segments.Climb as climb_segment
import Sizing.MissionProfile.Segments.Takeoff as takeoff_segment
import Sizing.MissionProfile.Segments.approach as approach_segment
import Sizing.MissionProfile.Segments.landing as landing_segment
import Sizing.MissionProfile.Segments.Taxi as taxi_segment
import Sizing.utils.utils as utils


def example():

    ## Ewxample of a mission profile (given in the project)
    segments_list = []
    ### taxi ###
    taxi = taxi_segment.Taxi(
        time=20,
        percent_fuel_flow=0.1,
        weight_fraction=1,
        speed=15,
        altitude=0,
        phase_number=1,
        name="Taxi_out",
    )
    segments_list.append(taxi)
    ### Takeoff ###
    takeoff = takeoff_segment.Takeoff(
        takeoff_distance=5500,
        weight_fraction=taxi.weight_fraction.value,  ## Initial guess for the weight fraction , will be updated during the mission analysis
        obstacle_height=35,
        phase_number=2,
        name="Takeoff",
    )
    segments_list.append(takeoff)
    first_climb = climb_segment.climb(
        phase_number=3,
        climb_rate=3000,
        KEAS=250,
        start_altitude=0,
        end_altitude=10000,
        time=None,  ### useless for now
        weight_fraction=takeoff.weight_fraction.value,  ## Initial guess for the weight fraction , will be updated during the mission analysis
        name="First_climb",
    )
    segments_list.append(first_climb)

    ### Horizontal Acceleration ###
    acceleration1 = acceleration_segment.acceleration(
        KEAS_start=250,
        KEAS_end=290,
        time=60,
        weight_fraction=first_climb.weight_fraction.value,
        altitude=10000,
        phase_number=4,
        name="First Acceleration",
    )
    segments_list.append(acceleration1)
    ### Climb to crossover ###
    Goal_Mach = 0.78
    climb_to_crossover = climb_segment.climb(
        start_altitude=10000,
        end_altitude=utils.crossover_altitude(Goal_Mach, 290),
        climb_rate=3000,
        KEAS=290,
        time=None,
        weight_fraction=acceleration1.weight_fraction.value,
        phase_number=5,
        name="Climb to crossover",
    )
    segments_list.append(climb_to_crossover)

    ### Climb to cruise ###
    climb_to_cruise = climb_segment.climb(
        climb_rate=1500,
        start_altitude=utils.crossover_altitude(Goal_Mach, 290),
        end_altitude=35000,
        time=None,
        weight_fraction=climb_to_crossover.weight_fraction.value,
        KEAS=None,
        MACH=0.78,
        phase_number=6,
        name="Climb to cruise",
    )
    segments_list.append(climb_to_cruise)

    # ### Cruise ###
    cruise = cruise_segment.cruise(
        altitude=35000,
        range=3000,
        weight_fraction=1,
        EAS=None,
        Mach=0.78,
        bank_angle=0,
        phase_number=7,
        name="Main Cruise",
    )
    segments_list.append(cruise)
    ###PHASE 8-10 NO fuel flow##
    descent1 = climb_segment.climb(
        start_altitude=35000,
        end_altitude=3000,
        climb_rate=-1500,
        time=None,
        weight_fraction=cruise.weight_fraction.value,
        KEAS=250,
        MACH=None,
        phase_number=8,
        name="Descent 1",
    )
    segments_list.append(descent1)
    ##Phase 9 deceleration###
    deceleration1 = acceleration_segment.acceleration(
        KEAS_start=250,
        KEAS_end=135,
        time=60,
        altitude=3000,
        weight_fraction=descent1.weight_fraction.value,
        phase_number=9,
        name="Deceleration 1",
    )
    segments_list.append(deceleration1)

    ### Phase 10 : Approach ###
    approach = approach_segment.approach(
        flight_path_angle=3,
        start_altitude=3000,
        end_altitude=0,
        weight_fraction=deceleration1.weight_fraction.value,
        KEAS=135,
        percent_fuel_flow=0.20,
        phase_number=10,
        name=" first Approach",
    )
    segments_list.append(approach)
    go_around = takeoff_segment.Takeoff(
        takeoff_distance=5500,
        weight_fraction=approach.weight_fraction.value,
        obstacle_height=0,
        phase_number="11a",
        name="Go around",
    )
    segments_list.append(go_around)

    ## climb to 15 000 ft AT 3000 ft/min
    climb_to_15000 = climb_segment.climb(
        climb_rate=3000,
        KEAS=250,
        start_altitude=0,
        end_altitude=15000,
        time=None,
        weight_fraction=approach.weight_fraction.value,
        phase_number="11b",
        name="go_around Climb to 15000",
    )
    segments_list.append(climb_to_15000)
    ### Phase 12 : Cruise_2 ###
    cruise2 = cruise_segment.cruise(
        altitude=15000,
        range=200,
        weight_fraction=climb_to_15000.weight_fraction.value,
        EAS=250,
        Mach=None,
        bank_angle=0,
        phase_number="12",
        name="Cruise 2",
    )
    segments_list.append(cruise2)

    ## Phase 13 : Loiter
    loiter_seg = cruise_segment.Loiter(
        altitude=15000,
        weight_fraction=cruise2.weight_fraction.value,
        time=45,
        phase_number="13",
        name="Loiter for 45 min",
    )
    segments_list.append(loiter_seg)
    ## Phase 14 : Descent 2
    descent2 = climb_segment.climb(
        start_altitude=15000,
        end_altitude=3000,
        climb_rate=-1500,
        time=None,
        weight_fraction=loiter_seg.weight_fraction.value,
        KEAS=250,
        MACH=None,
        phase_number="14",
        name="Descent 2",
    )
    segments_list.append(descent2)
    ## Phase 15 : Deceleration 2
    deceleration2 = acceleration_segment.acceleration(
        KEAS_start=250,
        KEAS_end=135,
        time=60,
        altitude=3000,
        weight_fraction=descent2.weight_fraction.value,
        phase_number="15",
        name="Deceleration 2",
    )
    segments_list.append(deceleration2)
    ## Phase 16 : Approach 2
    approach2 = approach_segment.approach(
        flight_path_angle=3,
        start_altitude=3000,
        end_altitude=0,
        weight_fraction=deceleration2.weight_fraction.value,
        KEAS=135,
        percent_fuel_flow=0.20,
        phase_number="16",
        name="Second Approach",
    )
    segments_list.append(approach2)
    ## Phase 17 : Landing
    landing = landing_segment.landing(
        KEAS=135,
        weight_fraction=approach2.weight_fraction.value,
        Cl_max=3,
        k_land=1.2,
        phase_number="17",
        name="Landing",
    )
    segments_list.append(landing)
    taxi_in = taxi_segment.Taxi(
        time=20,
        percent_fuel_flow=0.1,
        weight_fraction=1,
        speed=15,
        altitude=0,
        phase_number="18",
        name="Taxi_in",
    )
    segments_list.append(taxi_in)
    return segments_list
