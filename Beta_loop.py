import numpy as np
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
    WSR = WSR_guess
    TWR = TWR_guess
    WSR_old = WSR_guess
    TWR_old = TWR_guess
    betas_list = []

    for i in range(max_iteration):
        tqdm.write(f"Starting iteration {i} for Beta loop, WSR: {WSR}, TWR: {TWR}")
        betas_list = Main_Mission_Parametric.Compute_Mission_Profile_Parametric(
            WSR, TWR, segments_list=segments_list
        )
        constraints = Constraints_Parametric.constraint_analysis_main(
            segments_list, plot=False
        )
        WSR = constraints[0]
        TWR = constraints[1]
        if np.abs(WSR - WSR_old) < tolerance and np.abs(TWR - TWR_old) < tolerance:
            print(f"Convergence reached at iteration {i}")
            print(f"WSR final: {WSR}, TWR final: {TWR}")
            break
        WSR_old = WSR
        TWR_old = TWR
    return WSR, TWR, segments_list, betas_list[-1], betas_list, constraints


def gamma(WTO):
    kwe = Aircraft.Structure.KWE.value
    return kwe / (WTO**0.06)


def main_loop(
    Mission,
    WC,
    WP,
    guess_WTO,
    max_iteration=20,
    tolerance=0.001,
    WSR_guess=110,
    TWR_guess=0.3,
):
    iter_beta = Iter_Beta(Mission, max_iteration, tolerance, WSR_guess, TWR_guess)
    Beta_final = iter_beta[3]
    WSR = iter_beta[0]
    TWR = iter_beta[1]
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
    return (WTO, WSR, TWR, Beta_final, list_betas, constraints)
