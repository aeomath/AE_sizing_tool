from Sizing.Variable_info.Variable import Variable
import Sizing.utils.utils as utils
import Sizing.aerodynamics.Assumptions as aerodynamics
import Sizing.propulsion.assumptions as propulsion
from Sizing.utils.atmosphere import Atmosphere
import numpy as np
import Sizing.utils.Constants as const


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

    def Thrust_weight_ratio(
        self,
        wing_loading,
    ):
        # print("Cruising segment")
        load_factor = 1 / np.cos(self.bank_angle.value * np.pi / 180)
        beta = self.weight_fraction.value
        altitude = self.altitude.value
        if self.EAS.value is not None:
            EAS = self.EAS.value
            Mach = utils.KEAS_to_Mach(EAS, altitude)
        elif self.Mach.value is not None:
            Mach = self.Mach.value
            EAS = utils.Mach_to_KEAS(Mach, altitude)

        alpha = propulsion.thrust_lapse(Mach, Atmosphere(altitude).density_ratio.value)
        q = 0.5 * Atmosphere(0).density_slug_ft3.value * utils.knots_to_fts(EAS) ** 2
        Cd0 = aerodynamics.Cd0(Mach, altitude)
        K1 = aerodynamics.K1
        K2 = aerodynamics.K2
        linear_term = K1 * (beta / q) * wing_loading
        Inverse_ter = Cd0 / ((beta / q) * wing_loading)
        T_W = (beta / alpha) * (
            linear_term * load_factor**2 + K2 * load_factor + Inverse_ter
        )
        return T_W
