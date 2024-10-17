import numpy as np

"""
This module contains functions for iterating over beta values and computing the 
weight take-off (WTO) for an aircraft sizing tool.
Functions:
    Iter_Beta(segments_list: List[segments], max_iteration=20, tolerance=0.001, 
              WSR_guess=110, TWR_guess=0.3) -> Tuple[float, float, List[segments], float, List[float], List[float]]:
        Iterates over beta values to compute the Wing Loading (WSR) and Thrust-to-Weight Ratio (TWR).
    gamma(WTO: float) -> float:
        Computes the gamma value based on the weight take-off (WTO).
    main_loop(Mission: List[segments], WC: float, WP: float, guess_WTO: float, 
              max_iteration=20, tolerance=0.001, WSR_guess=110, TWR_guess=0.3) -> Tuple[float, float, float, float, List[float], List[float], List[segments]]:
        Main loop for computing the weight take-off (WTO) by iterating over beta values and updating segments.
"""
from Sizing.Variable_info.variables import Aircraft
from Sizing.Mission_analysis import Main_Mission_Parametric
from Sizing.constraint_analysis import Constraints_Parametric
from Sizing.MissionProfile.segments import segments
from tqdm import tqdm
from typing import List


def Iter_Beta(
    segments_list: List[segments],
    max_iteration=20,
    tolerance=0.001,
    WSR_guess=110,
    TWR_guess=0.3,
):
    """
    Iteratively computes the Wing Loading (WSR) and Thrust-to-Weight Ratio (TWR)
    for a given mission profile until convergence is reached or the maximum number
    of iterations is exceeded. See report section III.A for more details.
    Args:
        segments_list (List[segments]): List of mission segments.
        max_iteration (int, optional): Maximum number of iterations. Defaults to 20.
        tolerance (float, optional): Convergence tolerance for WSR and TWR. Defaults to 0.001.
        WSR_guess (float, optional): Initial guess for Wing Loading (WSR). Defaults to 110.
        TWR_guess (float, optional): Initial guess for Thrust-to-Weight Ratio (TWR). Defaults to 0.3.
    Returns:
        tuple: A tuple containing:
            - WSR (float): Final Wing Loading after convergence.
            - TWR (float): Final Thrust-to-Weight Ratio after convergence.
            - updated_segments_list (List[segments]): Updated list of mission segments.
            - last_beta (float): Last computed beta value.
            - betas_list (List[float]): List of all computed beta values.
            - constraints (List[float]): List of constraint values from the last iteration.
    """

    WSR = WSR_guess
    TWR = TWR_guess
    WSR_old = WSR_guess
    TWR_old = TWR_guess
    betas_list = []

    for i in range(max_iteration):
        tqdm.write(f"Starting iteration {i} for Beta loop, WSR: {WSR}, TWR: {TWR}")
        betas_list, updated_segments_list = (
            Main_Mission_Parametric.Compute_Mission_Profile_Parametric(
                WSR, TWR, segments_list
            )
        )
        # betas_updated = [self.weight_fraction.value for self in updated_segments_list]
        # print(f"Betas_updated: {betas_updated}")
        constraints = Constraints_Parametric.constraint_analysis_main(
            updated_segments_list, plot=False
        )
        segments_list = updated_segments_list
        WSR = constraints[0]
        TWR = constraints[1]
        if np.abs(WSR - WSR_old) < tolerance and np.abs(TWR - TWR_old) < tolerance:
            print(f"Convergence reached at iteration {i}")
            print(f"WSR final: {WSR}, TWR final: {TWR}")
            break
        WSR_old = WSR
        TWR_old = TWR
        # print("beta list", betas_list)
        # print(
        #     "Betas_updated",
        #     [self.weight_fraction.value for self in updated_segments_list],
        # )
    return WSR, TWR, updated_segments_list, betas_list[-1], betas_list, constraints


def gamma(WTO):
    """
    Calculate the gamma value based on the given weight take-off (WTO).
    see report section III.A for more details.
    Parameters:
    WTO (float): Weight take-off value.
    Returns:
    float: Calculated gamma value.
    """
    kwe = Aircraft.Structure.KWE.value
    return kwe / (WTO**0.06)


def main_loop(
    Mission: List[segments],
    WC,
    WP,
    guess_WTO,
    max_iteration=20,
    tolerance=0.001,
    WSR_guess=110,
    TWR_guess=0.3,
):

    iter_beta = Iter_Beta(Mission, max_iteration, tolerance, WSR_guess, TWR_guess)

    WSR = iter_beta[0]
    TWR = iter_beta[1]
    updated_segments_list = iter_beta[2]
    Beta_final = iter_beta[3]
    list_betas = iter_beta[4]
    constraints = iter_beta[5]

    def WTO_computed(beta, WC, WP, WTO):
        return (WC + WP) / (1 - 1.06 * (1 - beta) - gamma(WTO))

    for i in range(max_iteration):
        WTO = WTO_computed(Beta_final, WC, WP, guess_WTO)
        # print(f"Iteration {i} WTO")
        if np.abs(WTO - guess_WTO) < 1:
            print(f"Convergence WTO reached at iteration {i}")
            break
        guess_WTO = WTO
    return (WTO, WSR, TWR, Beta_final, list_betas, constraints, updated_segments_list)
