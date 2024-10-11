from Sizing.propulsion.assumptions import thrust_lapse, TSFC
from Sizing.Variable_info.variables import Aircraft
from Sizing.aerodynamics.Assumptions import Cd0, Cdi
from Sizing.utils.atmosphere import Atmosphere
from Sizing.utils.utils import KEAS_to_Mach
import numpy as np
import matplotlib.pyplot as plt
import Sizing.utils.utils as utils
from Sizing.constraint_analysis import constraint
from Sizing.Mission_analysis import Main_mission_analysis


def kg_m2_to_lb_ft2(kg_m2):
    lb_ft2 = kg_m2 * 0.204816
    return lb_ft2


def lb_ft2_to_kg_m2(lb_ft2):
    kg_m2 = lb_ft2 * 4.88243
    return kg_m2


##constraint.constraint_analysis_main(plot=True)
Main_mission_analysis.Mission_analysis(125, 0.3)
