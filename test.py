from Sizing.propulsion.assumptions import thrust_lapse, TSFC
from Sizing.Variable_info.variables import Aircraft
from Sizing.aerodynamics.Assumptions import Cd0, Cdi
from Sizing.utils.atmosphere import Atmosphere
from Sizing.utils.utils import KEAS_to_Mach
import numpy as np
import matplotlib.pyplot as plt
import Sizing.utils.utils as utils
from Sizing.constraint_analysis import Constraints_Parametric
from Sizing.Mission_analysis import Main_Mission_Parametric
from Sizing.MissionProfile.segments import segments


print(Aircraft.Aerodynamics.K1)
print(Aircraft.Propulsion.ktsfc)
print(Aircraft.Aerodynamics.K2)
print(Aircraft.Structure.KWE)
print(len(Aircraft.Design.Weight_fractions.value))
