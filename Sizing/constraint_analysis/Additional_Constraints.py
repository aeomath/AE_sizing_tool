import Sizing.MissionProfile.Segments as Mission_segments
import Sizing.utils.Constants as const
import Sizing.MissionProfile.Segments.acceleration as acceleration_segment
import Sizing.MissionProfile.Segments.Cruise as cruise_segment
import Sizing.MissionProfile.Segments.Climb as climb_segment
import Sizing.MissionProfile.Segments.Takeoff as takeoff_segment
import Sizing.MissionProfile.Segments.approach as approach_segment
import Sizing.MissionProfile.Segments.landing as landing_segment
from typing import List
from Sizing.MissionProfile.segments import segments
import numpy as np


def Additional_constraints(
    name_list,
    Thruts_Weight_ratios_list: list,
    Wing_loading,
    Weight_fraction_top_of_climb=0.95,
):
    ### Service Ceiling ###

    service_ceiling = 41000
    Mach = 0.78
    ceiling = climb_segment.climb(
        climb_rate=300,
        start_altitude=service_ceiling,
        end_altitude=service_ceiling,
        time=100,
        weight_fraction=Weight_fraction_top_of_climb,
        KEAS=None,
        MACH=Mach,
        name="Service Ceiling",
    )
    name_list.append(ceiling.name)
    Thruts_Weight_ratios_list.append(ceiling.Thrust_Weight_Ratio(Wing_loading))

    ### Maximum Mach Number ###
    max_Mach = 0.82
    maximum_mach_segment = cruise_segment.cruise(
        altitude=35000,
        range=500,
        weight_fraction=Weight_fraction_top_of_climb,
        Mach=max_Mach,
        name="Maximum Mach Number",
    )
    name_list.append(maximum_mach_segment.name)
    Thruts_Weight_ratios_list.append(
        maximum_mach_segment.Thrust_Weight_Ratio(Wing_loading)
    )

    ### Steep Turn ###
    turn_segment = cruise_segment.cruise(
        altitude=39000,
        range=500,
        weight_fraction=Weight_fraction_top_of_climb,
        Mach=0.78,
        bank_angle=45,
        name="Steep Turn",
    )
    name_list.append(turn_segment.name)
    Thruts_Weight_ratios_list.append(turn_segment.Thrust_Weight_Ratio(Wing_loading))

    ### Climb with one engine ###
    takeoff_one_engine = takeoff_segment.Takeoff(5500, 1, kt0=1.2)

    gradient_percent = 0.05
    path_angle = np.arctan(gradient_percent) * 180 / np.pi
    takeoff_speed = takeoff_one_engine.takeoff_EAS_speed(Wing_loading) * 1.2
    climb_one_engine_segment = climb_segment.climb(
        KEAS=takeoff_speed,
        start_altitude=0,
        end_altitude=3000,
        time=None,
        weight_fraction=1,  ## Worst case scenario
        flight_path_angle=path_angle,
        name="Climb with one engine",
    )
    name_list.append(climb_one_engine_segment.name)
    Thruts_Weight_ratios_list.append(
        2 * climb_one_engine_segment.Thrust_Weight_Ratio(Wing_loading)
    )
    return name_list, Thruts_Weight_ratios_list
