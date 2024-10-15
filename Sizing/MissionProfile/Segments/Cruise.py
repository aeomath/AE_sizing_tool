from Sizing.Variable_info.Variable import Variable
import Sizing.utils.utils as utils
import Sizing.aerodynamics.Assumptions as aerodynamics
import Sizing.propulsion.assumptions as propulsion
from Sizing.utils.atmosphere import Atmosphere
import numpy as np
import Sizing.utils.Constants as const
from Sizing.MissionProfile.segments import segments


class cruise(segments):
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
        self,
        altitude,
        range,
        weight_fraction,
        EAS=None,
        Mach=None,
        bank_angle=0,
        phase_number=-1,
        name=None,
        is_additional_constraint=False,
    ):
        super().__init__(
            "Cruise",
            phase_number=phase_number,
            weight_fraction=weight_fraction,
            name=name,
        )
        self.altitude = Variable("altitude", altitude, "ft", "Cruise altitude")
        if EAS is None and Mach is None:
            raise ValueError("Either Mach or EAS must be provided,you provided none")
        if EAS is not None and Mach is not None:
            print("EAS is ", EAS)
            print("Mach is ", Mach)
            raise ValueError("Either Mach or EAS must be provided,but not both")
        self.Mach = Variable("Mach", Mach, "", "Cruise Mach number")
        self.EAS = Variable("EAS", EAS, "KEAS", "Cruise EAS")
        self.range = Variable("range", range, "Nmi", "Cruise range")
        self.bank_angle = Variable("bank_angle", bank_angle, "deg", "Bank angle")
        self.is_additional_constraint = is_additional_constraint

    def Thrust_Weight_Ratio(
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

    def Mach_number(self):
        if self.Mach.value is not None:
            return self.Mach.value
        elif self.EAS.value is not None:
            return utils.KEAS_to_Mach(self.EAS.value, self.altitude.value)

    def EAS_knots(self):
        if self.EAS.value is not None:
            return self.EAS.value
        elif self.Mach.value is not None:
            return utils.Mach_to_KEAS(self.Mach.value, self.altitude.value)

    def TAS_knots(self):
        if self.Mach.value is not None:
            return utils.Mach_to_TAS(self.Mach.value, self.altitude.value)
        elif self.EAS.value is not None:
            return utils.KEAS_to_TAS(self.EAS.value, self.altitude.value)

    def Cl(self, wing_loading):
        q = (
            0.5
            * Atmosphere(0).density_slug_ft3.value
            * utils.knots_to_fts(self.EAS_knots()) ** 2
        )
        return (wing_loading * self.weight_fraction.value) / q

    def Cd0(self):
        if self.Mach.value is not None:
            return aerodynamics.Cd0(0, self.altitude.value)
        elif self.EAS.value is not None:
            return aerodynamics.Cd0(
                utils.KEAS_to_Mach(self.EAS.value, self.altitude.value),
                self.altitude.value,
            )

    def Cd(self, wing_loading):
        return (
            self.Cd0()
            + aerodynamics.K1 * self.Cl(wing_loading) ** 2
            + aerodynamics.K2 * self.Cl(wing_loading)
        )

    def thrust_lapse(self):
        if self.Mach.value is not None:
            return propulsion.thrust_lapse(
                self.Mach.value, Atmosphere(self.altitude.value).density_ratio.value
            )
        elif self.EAS.value is not None:
            return propulsion.thrust_lapse(
                utils.KEAS_to_Mach(self.EAS.value, self.altitude.value),
                Atmosphere(self.altitude.value).density_ratio.value,
            )

    def tsfc(self):
        altitude = self.altitude.value
        theta = Atmosphere(altitude).temperature_ratio.value
        if self.Mach.value is not None:
            return propulsion.TSFC(self.Mach.value, theta)
        elif self.EAS.value is not None:
            return propulsion.TSFC(utils.KEAS_to_Mach(self.EAS.value, altitude), theta)

    def wf_wi(self, WSR, TWR=None):
        delta_s = utils.nmi_to_ft(self.range.value)
        TAS_fts = utils.knots_to_fts(self.TAS_knots())
        # print(TAS_fts)
        Cd = self.Cd(WSR)
        Cl = self.Cl(WSR)
        # print(Cl)
        return np.exp(-self.tsfc() / TAS_fts * delta_s * Cd / Cl)


class Loiter(segments):
    def __init__(self, altitude, weight_fraction, time, phase_number=-1, name=None):
        super().__init__(
            "Loiter",
            phase_number=phase_number,
            weight_fraction=weight_fraction,
            name=name,
        )
        self.altitude = Variable("altitude", altitude, "ft", "Loiter altitude")
        self.time = Variable("time", time, "min", "Loiter time")

    ### Best L/D speed calculation

    def iter_best_L_D_speed_EAS(self, Wing_Loading):
        # print("getting best L/D speed...")
        ### best lift to drag speed
        def Best_L_D_speed_EAS(Wing_Loading, Cd0, beta):  ### best lift to drag speed
            K = aerodynamics.K1
            return np.sqrt(
                (2 / (Atmosphere(0).density_slug_ft3.value))
                * Wing_Loading
                * beta
                * np.sqrt(K / Cd0)
            )

        altitude = self.altitude.value
        beta = self.weight_fraction.value
        tolerance = 1e-3
        max_iterations = 50
        Mach = 0.5

        for i in range(max_iterations):
            Cd0 = aerodynamics.Cd0(Mach, altitude)
            speed_fts = Best_L_D_speed_EAS(Wing_Loading, Cd0, beta)
            speed = utils.fts_to_knots(speed_fts)
            new_Mach = utils.KEAS_to_Mach(speed, altitude)
            if np.all(abs(new_Mach - Mach) < tolerance):
                break
            Mach = new_Mach
        return speed

    def tsfc(self, Wing_Loading):
        altitude = self.altitude.value
        EAS = self.iter_best_L_D_speed_EAS(Wing_Loading)
        theta = Atmosphere(altitude).temperature_ratio.value
        return propulsion.TSFC(utils.KEAS_to_Mach(EAS, altitude), theta)

    def Cd0(self, WSR):
        EAS = self.iter_best_L_D_speed_EAS(WSR)
        return aerodynamics.Cd0(
            utils.KEAS_to_Mach(EAS, self.altitude.value),
            self.altitude.value,
        )

    def wf_wi(self, WSR, TWR):
        return np.exp(
            -self.tsfc(WSR)
            * self.time.value
            * 60
            * (aerodynamics.K2 + np.sqrt(4 * self.Cd0(WSR) * aerodynamics.K1))
        )

    def Thrust_Weight_Ratio(self, wing_loading):
        beta = self.weight_fraction.value
        altitude = self.altitude.value
        EAS = self.iter_best_L_D_speed_EAS(wing_loading)
        Mach = utils.KEAS_to_Mach(EAS, altitude)
        alpha = propulsion.thrust_lapse(Mach, Atmosphere(altitude).density_ratio.value)
        q = 0.5 * Atmosphere(0).density_slug_ft3.value * utils.knots_to_fts(EAS) ** 2
        Cd0 = aerodynamics.Cd0(Mach, altitude)
        K1 = aerodynamics.K1
        K2 = aerodynamics.K2
        linear_term = K1 * (beta / q) * wing_loading
        Inverse_term = Cd0 / ((beta / q) * wing_loading)
        T_W = (beta / alpha) * (linear_term + K2 + Inverse_term)
        return T_W
