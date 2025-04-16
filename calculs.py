# calculs.py
import numpy as np

def calculer_coefficient_diffusion(D_AB_initial, D_BA_initial, fraction_A, coef_lambda_A, coef_lambda_B, q_A, q_B, theta_A, theta_B, theta_BA, theta_AB, theta_AA, theta_BB, tau_AB, tau_BA, D_exp):
    if fraction_A <= 0 or fraction_A >= 1:
        raise ValueError("La fraction molaire de A doit être entre 0 et 1 (exclus).")
    if coef_lambda_A <= 0 or coef_lambda_B <= 0:
        raise ValueError("Les coefficients lambda doivent être strictement positifs.")
    if tau_AB <= 0 or tau_BA <= 0:
        raise ValueError("Les valeurs de tau doivent être strictement positives.")

    fraction_B = 1 - fraction_A
    phi_A = fraction_A * coef_lambda_A / (fraction_A * coef_lambda_A + fraction_B * coef_lambda_B)
    phi_B = fraction_B * coef_lambda_B / (fraction_A * coef_lambda_A + fraction_B * coef_lambda_B)

    terme1 = fraction_B * np.log(D_AB_initial) + fraction_A * np.log(D_BA_initial) + 2 * (fraction_A * np.log(fraction_A / phi_A) + fraction_B * np.log(fraction_B / phi_B))
    terme2 = 2 * fraction_A * fraction_B * ((phi_A / fraction_A) * (1 - (coef_lambda_A / coef_lambda_B)) + (phi_B / fraction_B) * (1 - (coef_lambda_B / coef_lambda_A)))
    terme3 = (fraction_B * q_A) * ((1 - theta_BA ** 2) * np.log(tau_BA) + (1 - theta_BB ** 2) * tau_AB * np.log(tau_AB))
    terme4 = (fraction_A * q_B) * ((1 - theta_AB ** 2) * np.log(tau_AB) + (1 - theta_AA ** 2) * tau_BA * np.log(tau_BA))

    ln_D_AB = terme1 + terme2 + terme3 + terme4 
    D_AB = np.exp(ln_D_AB)
    erreur_relative = abs((D_AB - D_exp)) / D_exp * 100

    return D_AB, erreur_relative
