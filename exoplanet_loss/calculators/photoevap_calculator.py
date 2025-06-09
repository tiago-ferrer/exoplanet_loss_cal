import math

G = 6.67430e-8  # gravitational constant [cm^3 g^-1 s^-2]
# n = 0.3
class PhotoevaporationCalculator:
    def __init__(self, n, L_x, R_p, M_p, a, e):
        self.n = n
        self.L_x = L_x
        self.R_p = R_p
        self.G = G
        self.M_p = M_p
        self.a = a
        self.e = e

    def get(self):
        return calculo_perda_fotoevaporacao(self.n, self.L_x, self.R_p, self.G, self.M_p, self.a,
                                                                 self.e)

def calculo_perda_fotoevaporacao(n, L_x, R_p, G, M_p, a, e):
    """
    Calcula a taxa de perda de massa por fotoevaporação.

    Parâmetros:
    -----------
    n : float
        Fator de eficiência variando entre 0.25 e 1
    L_x : float
        Luminosidade em raio X e EUV da estrela
    R_p : float
        Raio do planeta em cm
    G : float
        Constante gravitacional
    M_p : float
        Massa do planeta em gramas
    a : float
        Semieixo maior
    e : float
        Excentricidade

    Retorna:
    --------
    float
        Taxa de perda de massa por fotoevaporação

    Observações:
    ------
    Utiliza as seguintes relações:
    a_ = medida temporal da distância orbital (órbitas excêntricas <a>= a(1+0.5*e^2)
    K = 1 - 3/2E + 1/2E^3
    E = a_ ( (4*pi*d_p)/ (9* M_e))^(1/3)
    d_p = densidade do planeta em g/cm^3
    M_e = massa da estrela em gramas
    """
    return n * ((L_x*(R_p**3))/ (3*G*M_p*(calcular_a_(a,e)**2)))

def calcular_a_(a, e):
    """
    Calcula a medida temporal da distância orbital para órbitas excêntricas.

    Parâmetros:
    -----------
    a : float
        Semieixo maior
    e : float
        Excentricidade

    Retorna:
    --------
    float
        Medida temporal da distância orbital
    """
    return a * (1 + (0.5 * (e**2)))

def calcular_E(d_p, M_e, a_):
    """
    Calcula o parâmetro E usado no cálculo de fotoevaporação.

    Parâmetros:
    -----------
    d_p : float
        Densidade do planeta em g/cm^3
    M_e : float
        Massa da estrela em gramas
    a_ : float
        Medida temporal da distância orbital

    Retorna:
    --------
    float
        Parâmetro E
    """
    return a_ * ((4 * math.pi * d_p) / (9 * M_e))**(1/3)

def calcular_K(E):
    """
    Calcula o parâmetro K usado no cálculo de fotoevaporação.

    Parâmetros:
    -----------
    E : float
        Parâmetro E

    Retorna:
    --------
    float
        Parâmetro K
    """
    return 1 - (3/(2*E)) + (1/(2*(E**3)))