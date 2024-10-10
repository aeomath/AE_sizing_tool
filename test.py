from Sizing.propulsion.assumptions import thrust_lapse, TSFC
from Sizing.Variable_info.variables import Aircraft
from Sizing.aerodynamics.Assumptions import Cd0, Cdi
from Sizing.utils.atmosphere import Atmosphere
from Sizing.utils.utils import KEAS_to_Mach
from Sizing.constraint_analysis import climb, cruise, acceleration, approach_landing
import numpy as np
import matplotlib.pyplot as plt
import Sizing.utils.utils as utils
from Sizing.constraint_analysis import constraint


def kg_m2_to_lb_ft2(kg_m2):
    lb_ft2 = kg_m2 * 0.204816
    return lb_ft2


def lb_ft2_to_kg_m2(lb_ft2):
    kg_m2 = lb_ft2 * 4.88243
    return kg_m2


# print(kg_m2_to_lb_ft2(600))

# print(Aircraft.Design.TOW)
# print(Aircraft.Aerodynamics.K1)
# print(Aircraft.Propulsion.ktsfc)
# print(Cd0(0.8, 1000))
# print(Cdi(0.5))


# atm = Atmosphere(5000, meter=True)
# print(atm.altitude)
# print(atm.temperature)
# print(atm.pressure)
# print(atm.density)
# print(atm.density_slug_ft3)
# print(atm.speed_of_sound)
# print(atm.density_ratio)
# print(atm.pressure_ratio)
# print(atm.temperature_ratio)
# print(KEAS_to_Mach(300, 10000))

# wing_loading = np.linspace(1, 130, 1000)
# T_W = Thrust_weight_ratio(wing_loading)
# X = wing_loading
# plt.plot(X, T_W)
# plt.xlabel("Wing Loading")
# plt.ylabel("Thrust to Weight Ratio")
# plt.title("Thrust to Weight Ratio vs Wing Loading, takeoff")
# plt.fill_between(X, T_W, color="red", alpha=0.3, label="Impossible Region")
# plt.show()


# wing_loading = np.linspace(1, 130, 1000)
# T_W = climb.Thrust_to_weight_ratio(wing_loading, 0.9, 3000, 250)
# X = wing_loading
# plt.plot(X, T_W)
# plt.xlabel("Wing Loading")
# plt.ylabel("Thrust to Weight Ratio")
# plt.title("Thrust to Weight Ratio vs Wing Loading, takeoff")
# plt.fill_between(X, T_W, color="red", alpha=0.3, label="Impossible Region")
# plt.show()
constraint.constraint_analysis_main(plot=False)
import Sizing.constraint_analysis.takeoff as takeoff

print(takeoff.takeoff_EAS_speed(100, Clmax=2.56, kt0=1.2))
