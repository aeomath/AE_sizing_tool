import json
import Inputs.Mission_example as Mission_example
from Sizing.Variable_info.variables import Variable
import Sizing.MissionProfile.Segments.acceleration as acceleration_segment
import Sizing.MissionProfile.Segments.Cruise as cruise_segment
import Sizing.MissionProfile.Segments.Climb as climb_segment
import Sizing.MissionProfile.Segments.Takeoff as takeoff_segment
import Sizing.MissionProfile.Segments.approach as approach_segment
import Sizing.MissionProfile.Segments.landing as landing_segment
import Sizing.MissionProfile.Segments.Taxi as taxi_segment
import Sizing.utils.utils as utils
from Sizing.MissionProfile.segments import segments
from typing import List


def extract_attributes(segment):
    attributes = segment.__dict__.copy()
    attributes["type"] = segment.__class__.__name__.lower()
    ordered_attributes = {
        "name": attributes.pop("name"),
        "type": attributes.pop("type"),
        "weight_fraction": attributes.pop("weight_fraction").to_dict().get("value"),
    }

    # Convert Variable objects to dictionaries
    for key, value in attributes.items():
        if isinstance(value, Variable):
            attributes[key] = value.value
        elif isinstance(value, list):
            # Convert lists of Variables to lists of dictionaries
            attributes[key] = [v.value if isinstance(v, Variable) else v for v in value]

    ordered_attributes.update(attributes)
    return ordered_attributes


def generate_json(segment_list):
    """
    Generates a JSON file named 'inputs.json' containing mission data.
    Args:
        segment_list (list): A list of mission segments.
    Returns:
        None
    The function uses the `Mission_example.example()` method to retrieve mission segments,
    extracts attributes from each segment, and writes the data to 'inputs.json' in a
    formatted JSON structure.
    """
    mission_data = {"phases": [extract_attributes(segment) for segment in segment_list]}
    with open("Mission_Profile.json", "w") as f:
        json.dump(mission_data, f, indent=4)


def create_phase(phase_data):
    """
    Create a phase object based on the provided phase data.
    Parameters:
    phase_data (dict): A dictionary containing the phase data. The dictionary must include a "type" key
                       which specifies the type of phase. The remaining keys should match the parameters
                       required by the corresponding phase class.
    Returns:
    object: An instance of the corresponding phase class based on the "type" specified in phase_data.
    Raises:
    ValueError: If the "type" specified in phase_data is unknown.
    Supported phase types and their corresponding classes:
    - "taxi": taxi_segment.Taxi
    - "takeoff": takeoff_segment.Takeoff
    - "climb": climb_segment.Climb
    - "acceleration": acceleration_segment.Acceleration
    - "cruise": cruise_segment.Cruise
    - "approach": approach_segment.Approach
    - "landing": landing_segment.Landing
    - "loiter": cruise_segment.Loiter
    """

    phase_type = phase_data.pop("type")
    if phase_type == "taxi":
        return taxi_segment.Taxi(**phase_data)
    elif phase_type == "takeoff":
        return takeoff_segment.Takeoff(**phase_data)
    elif phase_type == "climb" or phase_type == "descent":
        return climb_segment.climb(**phase_data)
    elif phase_type == "acceleration" or phase_type == "deceleration":
        return acceleration_segment.acceleration(**phase_data)
    elif phase_type == "cruise":
        return cruise_segment.cruise(**phase_data)
    elif phase_type == "approach":
        return approach_segment.approach(**phase_data)
    elif phase_type == "landing":
        return landing_segment.landing(**phase_data)
    elif phase_type == "loiter":
        return cruise_segment.Loiter(**phase_data)
    else:
        raise ValueError(f"Unknown phase type: {phase_type}")


def load_payload_and_crew_requirements(json_file_path) -> dict:
    with open(json_file_path, "r") as json_file:
        data = json.load(json_file)
    return data


def generate_example_test():
    """
    Generates an example test by reading mission data from a JSON file and creating a list of phases.
    The function reads the mission data from "inputs.json" file, processes each phase in the mission data,
    and creates a list of phases using the `create_phase` function.
    Returns:
        list: A list of phases created from the mission data.
    """
    real_segments_list = Mission_example.example()
    generate_json(segment_list=real_segments_list)

    def example():
        with open("Mission_profile.json", "r") as f:
            mission_data = json.load(f)

        segments_list = []
        for phase_data in mission_data["phases"]:
            phase = create_phase(phase_data)
            segments_list.append(phase)

        return segments_list

    new_segments_list = example()
    for new_seg, real_segment in zip(new_segments_list, real_segments_list):
        assert new_seg == real_segment


def load_mission_profile(json_file_path) -> List:
    with open(json_file_path, "r") as json_file:
        data = json.load(json_file)
    segments_list = []
    for phase_data in data["phases"]:
        phase = create_phase(phase_data)
        segments_list.append(phase)
    return segments_list
