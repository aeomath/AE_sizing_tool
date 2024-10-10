from Sizing.Variable_info.Variable import Variable

"""
Calculate the thrust to weight ratio for takeoff with the given constraints 
"""
from Sizing.MissionProfile.Segments import Mission_segments
from Sizing.utils.atmosphere import Atmosphere
from Sizing.propulsion.assumptions import thrust_lapse, TSFC
import numpy as np
import Sizing.utils.Constants as const
import Sizing.utils.utils as utils

### Cl max for takeoff : 2.56 info on https://booksite.elsevier.com/9780340741528/appendices/data-a/default.htm
### Kt0
### Hypothethis; sea level


def s_obst():
    "Compute the distance to clear an obstacle"


### Slide 19
def Thrust_weight_ratio(
    Wing_loading,
    beta=1,  ## Takeoff so beta = 1
    Clmax=2.56,
    st0=5500,
    altitude=0,
    kt0=1.2,
    tr=3,
    hobst=35,
):
    """
    Calculate the thrust-to-weight ratio for takeoff.
    Parameters:
    beta (float): Weight fraction.
    Clmax (float): Maximum lift coefficient.
    Wing_loading (float): Wing loading.
    sg (float, optional): Ground roll distance in feet. Default is 5500 feet.
    altitude (float, optional): Altitude in feet. Default is 0 feet.
    kt0 (float, optional): Takeoff speed factor. Default is 1.2.
    Cl_max (float, optional): Maximum lift coefficient during takeoff. Default is 2.56.
    tr (float, optional): Thrust ratio. Default is 3.
    hobst (float, optional): Obstacle height in feet. Default is 35 feet.
    Returns:
    float: Thrust-to-weight ratio required for takeoff.
    """
    print("Taking off...")
    atm = Atmosphere(altitude)
    rho = atm.density_slug_ft3.value
    alpha = thrust_lapse(0, atm.density_ratio.value)
    # alpha = 0.8875
    # rho = 0.002047
    # rho  # Convert from slug/ft^3 to kg/m^3
    Vt0 = np.sqrt((kt0**2 * 2 * beta * Wing_loading) / (rho * Clmax))
    sr = tr * Vt0
    Rc = Vt0**2 / ((0.8 * kt0**2 - 1) * const.SL_GRAVITY_FT)
    theta_obs = np.arccos(1 - hobst / Rc)
    s_obst = Rc * np.sin(theta_obs)
    sg_time_thrust_ratio = (beta**2 * kt0**2 * Wing_loading) / (
        alpha * rho * Clmax * const.SL_GRAVITY_FT
    )
    return sg_time_thrust_ratio / (st0 - s_obst - sr)


def takeoff_EAS_speed(Wing_loading, Clmax, kt0, altitude=0, beta=1):
    """
    Calculate the takeoff speed.
    Parameters:
    Clmax (float): Maximum lift coefficient.
    Wing_loading (float): Wing loading.
    kt0 (float): Takeoff speed factor.
    altitude (float, optional): Altitude in feet. Default is 0 feet.
    Returns:
    float: Takeoff speed in knots.
    """
    atm = Atmosphere(altitude)
    rho = atm.density_slug_ft3.value
    Vt0 = np.sqrt((kt0**2 * 2 * beta * Wing_loading) / (rho * Clmax))
    TAS_Knots = utils.fts_to_knots(Vt0)
    return utils.TAS_to_KEAS(TAS_Knots, altitude)
