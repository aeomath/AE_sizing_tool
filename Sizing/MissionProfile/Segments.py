from Sizing.Variable_info.Variable import Variable
import Sizing.utils.utils as utils


class Mission_segments:
    class climb:
        """
        This class contains the variables for the climb and descent segments of the mission profile.
        If climb, climb_rate is positive, else if descent, climb_rate is negative.
        Attributes:
            climb_rate (Variable): Rate of climb in ft/min.
            KEAS (Variable): Equivalent airspeed . If none, Climb is at constant Mach number.
            MACH (Variable): Mach number. if none, Climb is at constant EAS.
            start_altitude (Variable): Start altitude.
            end_altitude (Variable): End altitude.
            time (Variable): Time of climb.
            weight_fraction (Variable): Weight fraction (beta) at the end of the phase.

        """

        def __init__(
            self,
            start_altitude,
            end_altitude,
            time,
            weight_fraction,
            KEAS=None,
            MACH=None,
            climb_rate=None,
            flight_path_angle=None,
        ):
            ### Check that either Mach or EAS is provided
            if KEAS is None and MACH is None:
                raise ValueError("Either Mach or EAS must be provided")
            if KEAS is not None and MACH is not None:
                raise ValueError("Either Mach or EAS must be provided")
            self.KEAS = Variable("KEAS", KEAS, "KEAS", "Equivalent airspeed")
            self.MACH = Variable("MACH", MACH, "", "Mach number")
            ## Check that either flight path angle or ROC is provided
            if climb_rate is None and flight_path_angle is None:
                raise ValueError(
                    "Either climb rate or flight path angle must be provided"
                )
            if climb_rate is not None and flight_path_angle is not None:
                raise ValueError(
                    "Either climb rate or flight path angle must be provided"
                )
            self.climb_rate = Variable("climb_rate", climb_rate, "m/s", "Rate of climb")
            self.flight_path_angle = Variable(
                "flight_path_angle", flight_path_angle, "deg", "Flight path angle"
            )
            self.start_altitude = Variable(
                "start_altitude", start_altitude, "ft", "Start altitude"
            )
            self.end_altitude = Variable(
                "end_altitude", end_altitude, "ft", "End altitude"
            )
            self.time = Variable("time", time, "s", "Time of climb")
            self.weight_fraction = Variable(
                "weight_fraction", weight_fraction, "", "Weight fraction (beta)"
            )

        def is_descent(self):
            return self.climb_rate < 0

    class cruise:
        """
        A class to represent the cruise segment of a mission profile.
        Attributes:
            altitude (Variable): The altitude at which the cruise is taking place.
            EAS (Variable): The equivalent airspeed of the aircraft during cruise.
            Mach (Variable): The Mach number of the aircraft during cruise.
            range (Variable): The range of the aircraft during cruise.
            weight_fraction (Variable): The weight fraction (beta) of the aircraft during cruise.
            bank_angle (Variable): The bank angle of the aircraft during cruise.
        Careful , can't have both Mach and EAS or none of them
        """

        def __init__(
            self, altitude, range, weight_fraction, EAS=None, Mach=None, bank_angle=0
        ):
            self.altitude = Variable("altitude", altitude, "ft", "Cruise altitude")
            if EAS is None and Mach is None:
                raise ValueError("Either Mach or EAS must be provided")
            if EAS is not None and Mach is not None:
                raise ValueError("Either Mach or EAS must be provided")
            if Mach:
                self.Mach = Variable("Mach", Mach, "", "Cruise Mach number")
                self.EAS = Variable(
                    "EAS", utils.Mach_to_KEAS(Mach, altitude), "", "Cruise EAS"
                )
            if EAS:
                self.EAS = Variable("EAS", EAS, "KEAS", "Cruise EAS")
                self.Mach = Variable(
                    "Mach", utils.KEAS_to_Mach(EAS, altitude), "", "Cruise Mach number"
                )
            self.range = Variable("range", range, "Nmi", "Cruise range")
            self.weight_fraction = Variable(
                "weight_fraction", weight_fraction, "", "Weight fraction (beta)"
            )
            self.bank_angle = Variable("bank_angle", bank_angle, "deg", "Bank angle")

    class Takeoff:
        """
        Represents the takeoff segment of a mission profile.
        Attributes:
            takeoff_distance (Variable): The distance required for takeoff, in feet.
            weight_fraction (Variable): The weight fraction (beta) during takeoff.
            obstacle_height (Variable): The height of the obstacle to clear during takeoff, in feet.
        Args:
            takeoff_distance (float): The distance required for takeoff, in feet.
            weight_fraction (float): The weight fraction (beta) during takeoff.
            obstacle_height (Variable, optional): The height of the obstacle to clear during takeoff, in feet. Defaults to 35 feet.
        """

        def __init__(
            self,
            takeoff_distance,
            weight_fraction,
            obstacle_height=Variable("obstacle_height", 35, "ft", "Height of obstacle"),
        ):
            self.takeoff_distance = Variable(
                "takeoff_distance", takeoff_distance, "ft", "Takeoff distance"
            )

            self.weight_fraction = Variable(
                "weight_fraction", weight_fraction, "", "Weight fraction (beta)"
            )
            self.obstacle_height = Variable(
                "obstacle_height", obstacle_height, "ft", "Height of obstacle"
            )

    class acceleration:
        def __init__(self, KEAS_start, KEAS_end, time, weight_fraction, altitude):
            self.KEAS_start = Variable(
                "KEAS_start", KEAS_start, "KEAS", "Start Equivalent airspeed"
            )
            self.KEAS_end = Variable(
                "KEAS_end", KEAS_end, "KEAS", "End Equivalent airspeed"
            )
            self.time = Variable("time", time, "s", "Time of acceleration")
            self.weight_fraction = Variable(
                "weight_fraction", weight_fraction, "", "Weight fraction (beta)"
            )
            self.altitude = Variable("altitude", altitude, "ft", "Altitude")

        def is_deceleration(self):
            return self.KEAS_start > self.KEAS_end

    class approach:
        def __init__(
            self,
            flight_path_angle,
            start_altitude,
            end_altitude,
            weight_fraction,
            KEAS,
        ):
            self.flight_path_angle = Variable(
                "flight_angle", flight_path_angle, "deg", "Flight angle"
            )
            self.start_altitude = Variable(
                "start_altitude", start_altitude, "ft", "Start altitude"
            )
            self.end_altitude = Variable(
                "end_altitude", end_altitude, "ft", "End altitude"
            )
            self.weight_fraction = Variable(
                "weight_fraction", weight_fraction, "", "Weight fraction (beta)"
            )
            self.KEAS = Variable("KEAS", KEAS, "KEAS", "Equivalent airspeed")

    class landing:
        def __init__(self, weight_fraction, KEAS, Cl_max, k_land):
            self.weight_fraction = Variable(
                "weight_fraction", weight_fraction, "", "Weight fraction (beta)"
            )
            self.KEAS = Variable("KEAS", KEAS, "KEAS", "Equivalent airspeed")
            self.Cl_max = Variable("Cl_max", Cl_max, "", "Max lift coefficient")
            self.k_land = Variable("k_land", k_land, "", "Landing speed factor")
