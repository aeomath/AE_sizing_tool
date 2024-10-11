import numpy as np
import Sizing.MissionProfile.Segments.acceleration as acceleration_segment
import Sizing.MissionProfile.Segments.Cruise as cruise_segment
import Sizing.MissionProfile.Segments.Climb as climb_segment
import Sizing.MissionProfile.Segments.Takeoff as takeoff_segment
import Sizing.MissionProfile.Segments.approach as approach_segment
import Sizing.MissionProfile.Segments.landing as landing_segment
import Sizing.MissionProfile.Segments.Taxi as taxi_segment
import Sizing.utils.utils as utils


def Mission_analysis(WSR, TWR):
    Betas = []
    ### taxi ###
    taxi = taxi_segment.Taxi(
        time=20, percent_fuel_flow=0.1, weight_fraction=1, taxi_speed=15, altitude=0
    )
    beta_taxi = taxi.wf_wi(TWR)
    Betas.append(beta_taxi)
    print("Taxi phase 1 :  ", beta_taxi)
    ### Takeoff ###
    takeoff = takeoff_segment.Takeoff(takeoff_distance=5500, weight_fraction=1)
    print("Takeoff: PI :  ", takeoff.wf_wi(WSR, TWR))
    beta_takeoff = beta_taxi * takeoff.wf_wi(WSR, TWR)
    print("Phase 2 ", beta_takeoff)
    Betas.append(beta_takeoff)

    ### Climb ###
    def test_accuracy():
        test_climb = climb_segment.climb(
            climb_rate=3000,
            KEAS=250,
            start_altitude=10000,
            end_altitude=10000,
            time=100,
            weight_fraction=beta_takeoff,
        )
        test_climb2 = climb_segment.climb(
            climb_rate=3000,
            KEAS=250,
            start_altitude=0,
            end_altitude=0,
            time=100,
            weight_fraction=beta_takeoff,
        )

        return test_climb.is_accurate(WSR, TWR) - test_climb2.is_accurate(WSR, TWR)

    print("Climb: accuracy :  ", test_accuracy())

    ## Subdivide the climb segment into 10 segments of 1000 ft each
    climb_segments = []
    first_climb = climb_segment.climb(
        climb_rate=3000,
        KEAS=250,
        start_altitude=0,
        end_altitude=100,
        time=1000,
        weight_fraction=beta_takeoff,
    )
    Beta_climb = first_climb.wf_wi(WSR, TWR) * beta_takeoff
    for i in range(1, 10):
        climb = climb_segment.climb(
            climb_rate=3000,
            KEAS=250,
            start_altitude=i * 1000,
            end_altitude=(i + 1) * 1000,
            time=100,
            weight_fraction=Beta_climb,
        )
        print(f"Climbing {i*1000} to {(i+ 1)*1000} fts: beta :  ", Beta_climb)
        Beta_climb *= climb.wf_wi(WSR, TWR)
        # climb_segments.append(climb)
    print("Beta Phase 3  ", Beta_climb)
    Betas.append(Beta_climb)

    ### Horizontal Acceleration ###
    first_leg_acceleration = acceleration_segment.acceleration(
        KEAS_start=250,
        KEAS_end=255,
        time=60,
        weight_fraction=Beta_climb,
        altitude=10000,
    )
    beta_acceleration = first_leg_acceleration.wf_wi(WSR, TWR) * Beta_climb
    for speed in range(255, 290):
        acceleration_seg = acceleration_segment.acceleration(
            KEAS_start=speed,
            KEAS_end=speed + 1,
            time=60,
            weight_fraction=beta_acceleration,
            altitude=10000,
        )
        beta_acceleration *= acceleration_seg.wf_wi(WSR, TWR)
        print(
            f"Acceleration from {speed} to {speed + 1} kts: beta :  ", beta_acceleration
        )
    print("Acceleration Phase 4: beta_final_acceleration1 :  ", beta_acceleration)
    Betas.append(beta_acceleration)
    ### Climb to crossover ###
    goal_mach = 0.78
    climb_to_crossover = climb_segment.climb(
        climb_rate=3000,
        start_altitude=10000,
        end_altitude=utils.crossover_altitude(goal_mach, 290),
        weight_fraction=beta_acceleration,
        time=100,
        KEAS=290,
        MACH=None,
    )
