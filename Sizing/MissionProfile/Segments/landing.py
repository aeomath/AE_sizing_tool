from Sizing.Variable_info.Variable import Variable
import Sizing.utils.utils as utils
from Sizing.utils.atmosphere import Atmosphere
from Sizing.MissionProfile.segments import segments


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
        Beta = self.weight_fraction_constraint.value
        return self.Cl_max.value * q / (Beta * self.k_land.value**2)

    def wf_wi(self, WSR, TWR):
        print("Landing segment : no fuel burned for phase", self.phase_number)
        return 1

    def Thrust_Weight_Ratio(self, WSR):
        print("Landing segment : no Thrust required for phase", self.phase_number)
        return 0 * WSR
