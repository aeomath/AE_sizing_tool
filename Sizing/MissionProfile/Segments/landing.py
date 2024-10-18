from Sizing.Variable_info.Variable import Variable
from Sizing.MissionProfile.segments import segments
import Sizing.utils.utils as utils
from Sizing.utils.atmosphere import Atmosphere
import Sizing.propulsion.assumptions as propulsion
import Sizing.aerodynamics.Assumptions as aerodynamics

"""
Landing segment of the mission profile. Assumed to be at sea level.
Attributes:
    KEAS (Variable): Equivalent airspeed.
    Cl_max (Variable): Maximum lift coefficient.
    k_land (Variable): Landing speed factor.
    weight_fraction_constraint (Variable): Weight fraction constraint applied for the landing.
Methods:
    landing_constraint():
        Calculates the landing constraint based on the weight fraction and other parameters.
    wf_wi(WSR, TWR):
        Returns the weight fraction for the landing segment, which is always 1 as no fuel is burned.
    Thrust_Weight_Ratio(WSR):
        Returns the thrust-to-weight ratio for the landing segment, which is always 0 as no thrust is required.
    alpha_seg(WSR):
        Calculates the thrust lapse rate for the landing segment at sea level.
    Cl(wing_loading=None):
        Calculates the lift coefficient for the landing segment.
    Cd(wing_loading=None):
        Calculates the drag coefficient for the landing segment.
    lift_drag_ratio(wing_loading):
        Calculates the lift-to-drag ratio for the landing segment.
    tsfc(wing_loading):
        Calculates the thrust specific fuel consumption for the landing segment.
import Sizing.utils.utils as utils
from Sizing.utils.atmosphere import Atmosphere
from Sizing.MissionProfile.segments import segments
import Sizing.propulsion.assumptions as propulsion
import Sizing.aerodynamics.Assumptions as aerodynamics
"""


class landing(segments):
    def __init__(
        self,
        weight_fraction,
        KEAS,
        Cl_max=3,
        k_land=1.3,
        phase_number=-1,
        name=None,
        weight_fraction_constraint=0.85,
    ):
        super().__init__(
            "Landing",
            phase_number=phase_number,
            weight_fraction=weight_fraction,
            name=name,
        )
        self.KEAS = Variable("KEAS", KEAS, "KEAS", "Equivalent airspeed")
        self.Cl_max = Variable("Cl_max", Cl_max, "", "Max lift coefficient")
        self.k_land = Variable("k_land", k_land, "", "Landing speed factor")
        self.weight_fraction_constraint = Variable(
            "weight_fraction_constraint",
            weight_fraction_constraint,
            "",
            "Weight fraction constraint applied for the landing",
        )

    def landing_constraint(self):
        q = (
            0.5
            * Atmosphere(0).density_slug_ft3.value
            * utils.knots_to_fts(self.KEAS.value) ** 2
        )
        ## Change the weight fraction constraint based on the weight fraction (see report VI.H)
        self.weight_fraction_constraint.value = 0.05 + 0.95 * self.weight_fraction.value
        Beta = self.weight_fraction_constraint.value
        return self.Cl_max.value * q / (Beta * self.k_land.value**2)

    def wf_wi(self, WSR, TWR):
        # print("Landing segment : no fuel burned for phase", self.phase_number)
        return 1

    def Thrust_Weight_Ratio(self, WSR):
        # print("Landing segment : no Thrust required for phase", self.phase_number)
        return 0 * WSR

    def alpha_seg(self, WSR):
        altitude = 0  ## Assumed to be at sea level
        return propulsion.thrust_lapse(utils.KEAS_to_Mach(self.KEAS.value, 0), 1)

    def Cl(self, wing_loading=None):
        return self.Cl_max.value / self.k_land.value**2

    def Cd(self, wing_loading=None):
        return (
            aerodynamics.Cd0(utils.KEAS_to_Mach(self.KEAS.value, 0), 0)
            + aerodynamics.K1 * self.Cl() ** 2
            + aerodynamics.K2 * self.Cl()
        )

    def lift_drag_ratio(self, wing_loading):
        return self.Cl() / self.Cd()

    def tsfc(self, wing_loading):
        return propulsion.TSFC(utils.KEAS_to_Mach(self.KEAS.value, 0), 1)
