import numpy as np
from Sizing.Variable_info.variables import Aircraft
from Sizing.Mission_analysis import Main_Mission_Parametric
from Sizing.constraint_analysis import Constraints_Parametric
from Sizing.MissionProfile.segments import segments
from gui import weight_breakdown


def Iter_Beta(
    segments_list, max_iteration=20, tolerance=0.001, WSR_guess=110, TWR_guess=0.3
):
    WSR = WSR_guess
    TWR = TWR_guess
    prev_betas_list = [1] * len(segments_list)
    ## Results from the previous run, to be used as initial guess
    for i in range(max_iteration):
        betas_list = Main_Mission_Parametric.Compute_Mission_Profile_Parametric(
            WSR, TWR, segments_list=segments_list
        )
        print(betas_list, prev_betas_list)
        betas_diff = np.abs(np.array(betas_list) - np.array(prev_betas_list))
        if np.all(betas_diff < tolerance):
            print(f"Convergence reached at iteration {i}")
            break

        prev_betas_list = betas_list

        WSR, TWR = Constraints_Parametric.constraint_analysis_main(
            segments_list, plot=False
        )
    final_segments_list = segments_list
    ### Constraint analysis with the final weight fractions, to get the final WSR and TWR.
    # Be careful, this function updates the weight fraction for some segments for additional
    # constraints, so the weight fraction of the last segment is not the final weight fraction
    # of the last segment
    WSR, TWR = Constraints_Parametric.constraint_analysis_main(segments_list, plot=True)
    # print(f"Final WSR: {WSR}, TWR: {TWR}")
    # print("Weight fractions: ", betas_list)

    return WSR, TWR, final_segments_list, betas_list[len(betas_list) - 1], betas_list
    ## This function updates the weight fraction of each segment


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

    def WTO_computed(beta, WC, WP, WTO):
        return (WC + WP) / (beta - gamma(WTO))

    for i in range(100):
        WTO = WTO_computed(Beta_final, WC, WP, guess_WTO)
        # print(WTO)
        if np.abs(WTO - guess_WTO) < 1:
            break
        guess_WTO = WTO
    return (WTO, WSR, TWR, Beta_final, list_betas)
