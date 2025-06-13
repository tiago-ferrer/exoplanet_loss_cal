import math


def calcular_taxa_perda_de_massa_interacao_vento_solar(R_p, p_w, u_w):
    """
    Calculate mass loss due to solar wind interaction.

    Parameters:
        R_p : float - planet radius [cm]
        p_w : float - wind density [g/cm^3]
        u_w : floate - wind velocity [cm/s]

    Returns:
        float - mass loss rate [g/s]
    """
    tx_perda_massa= 4 * math.pi * (R_p**2) * (u_w *100) * p_w #g/s
    return tx_perda_massa