from Sizing.MissionProfile.segments import segments
import Sizing.MissionProfile.Segments.acceleration as acceleration_segment
import Sizing.MissionProfile.Segments.Cruise as cruise_segment
import Sizing.MissionProfile.Segments.Climb as climb_segment
import Sizing.MissionProfile.Segments.Takeoff as takeoff_segment
import Sizing.MissionProfile.Segments.approach as approach_segment
import Sizing.MissionProfile.Segments.landing as landing_segment
import Sizing.MissionProfile.Segments.Taxi as taxi_segment
from typing import List
from tqdm import tqdm


def Compute_Beta_Climb(WSR, TWR, climb_leg: climb_segment.climb, step=500):
    """
    Computes the weight fraction (beta) for a climb segment of an aircraft mission profile.
    Parameters:
    WSR (float): Wing loading ratio.
    TWR (float): Thrust-to-weight ratio.
    climb_leg (climb_segment.climb): An instance of the climb_segment.climb class representing the climb segment.
    Returns:
    float: The weight fraction (beta) at the end of the climb segment.
    The function iterates through altitude increments of 500 feet from the start altitude to the end altitude
    of the climb segment. For each increment, it calculates the weight fraction using the wf_wi method of the
    climb_segment.climb class and updates the beta_climb value accordingly. The initial beta value comes from the segment given,
    The final beta_climb value is returned.
    """

    start_altitude = climb_leg.start_altitude.value
    end_altitude = climb_leg.end_altitude.value
    beta_climb = climb_leg.weight_fraction.value
    for i in tqdm(
        range(start_altitude, end_altitude, step),
        desc="Climbing_decomposition phase number " + str(climb_leg.phase_number),
        leave=False,
    ):
        climb = climb_segment.climb(
            climb_rate=climb_leg.climb_rate.value,
            KEAS=climb_leg.KEAS.value,
            start_altitude=i,
            end_altitude=i + step,
            time=climb_leg.time.value,
            weight_fraction=beta_climb,
            flight_path_angle=climb_leg.flight_path_angle.value,
            MACH=climb_leg.MACH.value,
        )
        beta_climb *= climb.wf_wi(WSR, TWR)
        # print(f"Climbing {i} to {i + step} fts: beta_end_of_leg :  ", beta_climb)
    return beta_climb


def Compute_Beta_Acceleration(
    WSR, TWR, accel_leg: acceleration_segment.acceleration, step=1
):
    """
    Computes the weight fraction (beta) for an acceleration segment of an aircraft mission profile.
    Parameters:
    WSR (float): Wing loading ratio.
    TWR (float): Thrust-to-weight ratio.
    accel_leg (acceleration_segment.acceleration): An instance of the acceleration_segment.acceleration class representing the acceleration segment.
    Returns:
    float: The weight fraction (beta) at the end of the acceleration segment.
    The function iterates through speed increments from the start speed to the end speed of the acceleration segment.
    For each increment, it calculates the weight fraction using the wf_wi method of the acceleration_segment.acceleration class and updates the beta_accel value accordingly.
    The initial beta value comes from the segment given. The final beta_accel value is returned.
    """

    start_speed = accel_leg.KEAS_start.value
    end_speed = accel_leg.KEAS_end.value
    beta_accel = accel_leg.weight_fraction.value
    for speed in tqdm(
        range(start_speed, end_speed, step),
        desc="Acceleration decomposition, phase number:" + str(accel_leg.phase_number),
        leave=False,
    ):
        acceleration = acceleration_segment.acceleration(
            KEAS_start=speed,
            KEAS_end=speed + step,
            time=accel_leg.time.value,
            weight_fraction=beta_accel,
            altitude=accel_leg.altitude.value,
        )
        beta_accel *= acceleration.wf_wi(WSR, TWR)
        # print(
        #     f"Accelerating from {speed} to {speed + step} kts: beta_end_of_leg :  ",
        #     beta_accel,
        # )
    return beta_accel


def Compute_Beta_Cruise(WSR, cruise_leg: cruise_segment.cruise, steps=10):
    """
    Computes the weight fraction (beta) for a cruise segment of an aircraft mission profile.
    Parameters:
    WSR (float): Wing loading ratio.
    TWR (float): Thrust-to-weight ratio.
    cruise_leg (cruise_segment.cruise): An instance of the cruise_segment.cruise class representing the cruise segment.
    Time_min (float): The time in minutes for which the cruise segment is to be simulated (useful if loiter).
    Returns:
    float: The weight fraction (beta) at the end of the cruise segment.
    The function calculates the weight fraction using the wf_wi method of the cruise_segment.cruise class and returns the beta_cruise value.
    """
    ranges_nmi = cruise_leg.range.value / steps
    beta_cruise = cruise_leg.weight_fraction.value
    for i in tqdm(
        range(steps),
        desc="Cruise decomposition :  phase number" + str(cruise_leg.phase_number),
        leave=False,
    ):
        cruise = cruise_segment.cruise(
            altitude=cruise_leg.altitude.value,
            range=ranges_nmi,
            weight_fraction=beta_cruise,
            EAS=cruise_leg.EAS.value,
            Mach=cruise_leg.Mach.value,
            bank_angle=cruise_leg.bank_angle.value,
        )
        beta_cruise *= cruise.wf_wi(WSR)
        # print(f"Cruising step {i} beta_end_of_leg :  ", beta_cruise)
        # print("From ", i * ranges_nmi, " to ", (i + 1) * ranges_nmi)
    return beta_cruise


def Compute_Beta_Approach(WSR, TWR, approach_leg: approach_segment.approach, steps=100):
    """
    Computes the weight fraction (beta) for an approach segment of an aircraft mission profile.
    Parameters:
    WSR (float): Wing loading ratio.
    TWR (float): Thrust-to-weight ratio.
    approach_leg (approach_segment.approach): An instance of the approach_segment.approach class representing the approach segment.
    Returns:
    float: The weight fraction (beta) at the end of the approach segment.
    The function calculates the weight fraction using the wf_wi method of the approach_segment.approach class and returns the beta_approach value.
    """
    start_altitude = approach_leg.start_altitude.value
    end_altitude = approach_leg.end_altitude.value
    beta_approach = approach_leg.weight_fraction.value
    for i in tqdm(
        range(start_altitude, end_altitude, -steps),
        desc="Approach decomposition. Phase number :" + str(approach_leg.phase_number),
        leave=False,
    ):
        approach_seg = approach_segment.approach(
            flight_path_angle=approach_leg.flight_path_angle.value,
            start_altitude=i,
            end_altitude=i - steps,
            weight_fraction=beta_approach,
            KEAS=approach_leg.KEAS.value,
            percent_fuel_flow=approach_leg.percent_fuel_flow.value,
        )
        # print(
        #     "Approaching step ",
        #     i,
        #     " to ",
        #     i - steps,
        #     "weight fraction",
        #     approach_seg.wf_wi(WSR, TWR),
        # )
        beta_approach *= approach_seg.wf_wi(WSR, TWR)
        # print(f"Approaching step {i} beta_end_of_leg :  ", beta_approach)
        # print("from ", i, " to ", i - steps)
    return beta_approach


def Compute_Mission_Profile_Parametric(
    WSR, TWR, segments_list: List[segments]
) -> float:
    """
    Computes the mission profile parametrically based on the given wing loading ratio (WSR) and thrust-to-weight ratio (TWR).
    Args:
        WSR (float): Wing loading ratio.
        TWR (float): Thrust-to-weight ratio.
        segments_list (list): List of segments class instances, each representing a segment of the mission profile.
    Returns:
        list: A list containing the mission profile parameters computed for each segment.
    """
    Beta = 1  ## Initial weight fraction
    Betas_list = []
    for i in tqdm(range(len(segments_list))):
        segments_list[i].weight_fraction.value = Beta
        match segments_list[i].type:
            case "Climb":
                if segments_list[i].is_additional_constraint:
                    Beta *= 1
                else:
                    Beta = Compute_Beta_Climb(WSR, TWR, segments_list[i], step=500)
            case "Cruise":
                if segments_list[i].is_additional_constraint:
                    Beta *= 1
                else:
                    Beta = Compute_Beta_Cruise(WSR, segments_list[i], steps=10)
            case "Approach":
                Beta = Compute_Beta_Approach(WSR, TWR, segments_list[i], steps=100)
            case "Acceleration":
                Beta = Compute_Beta_Acceleration(WSR, TWR, segments_list[i], step=5)
            case _:
                Beta *= float(segments_list[i].wf_wi(WSR, TWR))
        ##print for debugging, uncomment if needed
        # print(
        #     "Phase ",
        #     segments_list[i].phase_number,
        #     "type : ",
        #     segments_list[i].type,
        #     " Beta : ",
        #     Beta,
        #     "name : ",
        #     segments_list[i].name,
        # )
        Betas_list.append(float(Beta))
    return Betas_list
