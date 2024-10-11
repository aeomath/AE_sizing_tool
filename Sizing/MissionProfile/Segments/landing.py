from Sizing.Variable_info.Variable import Variable
import Sizing.utils.utils as utils
from Sizing.utils.atmosphere import Atmosphere


class landing:
    def __init__(self, weight_fraction, KEAS, Cl_max, k_land):
        self.weight_fraction = Variable(
            "weight_fraction", weight_fraction, "", "Weight fraction (beta)"
        )
        self.KEAS = Variable("KEAS", KEAS, "KEAS", "Equivalent airspeed")
        self.Cl_max = Variable("Cl_max", Cl_max, "", "Max lift coefficient")
        self.k_land = Variable("k_land", k_land, "", "Landing speed factor")

    def landing_constraint(self):
        q = (
            0.5
            * Atmosphere(0).density_slug_ft3.value
            * utils.knots_to_fts(self.KEAS.value) ** 2
        )
        Beta = self.weight_fraction.value
        return self.Cl_max.value * q / (Beta * self.k_land.value**2)
