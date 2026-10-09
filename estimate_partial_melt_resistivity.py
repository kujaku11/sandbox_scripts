"""
melts_mt.py

Python translation of Darcy Cordell's MELTS_MT MATLAB package
(darcycordell/MELTS_MT), estimating bulk electrical resistivity of a
partially molten rhyolitic system from a MELTS thermodynamic
parameterization, following Cordell et al. (2022).

TRANSLATION STATUS
-------------------
Faithfully translated (exact formulas, from the .m files provided):
    - MELTS_MT_Rho.m       -> melts_mt_rho()
    - MELTS_MT_MagmaRes.m  -> melts_mt_magma_res()
    - volfrac.m            -> volfrac()
    - melt_rho.m           -> melt_rho()               (all 7 flags/compositions)
    - MAL3.m               -> MAL3()                   (3-phase Modified Archie's Law)
    - MAL.m                -> MAL()                    (2-phase Modified Archie's Law)
    - MAL_solve_phi.m      -> MAL_solve_phi()           (inverse: solve for melt fraction)
    - HS.m                 -> HS()                      (Hashin-Shtrikman bounds)
    - HS_solve_phi.m       -> HS_solve_phi()            (inverse: solve for melt fraction)
    - Hashim et al. (2013) crystal resistivity formula (exact, verbatim)

    - Keppler.m            -> Keppler()                 (Sinmyo & Keppler 2017 /
                                Guo & Keppler 2019 / Klumbach & Keppler 2020,
                                aqueous volatile/brine phase conductivity)
    - fugacity_PitzerSterner.py (Withers, after Pitzer & Sterner 1994)
                           -> PS_volume() / PS_fugacity()
                                (H2O equation of state, used internally by
                                Keppler() to get fluid density)

NOT PORTED (utility, not on the main computation path):
    - InterX.m (generic curve-intersection finder) -- only used in the
      commented-out plotting/case-study block of MELTS_MT_MagmaRes.m.
      Can be added if you need it; omitted for now since it's not called
      by any active code path you've shared.

Units convention (matches the MATLAB code):
    T        : degrees Celsius
    P        : MPa
    H2O_sys  : wt% (total system water)
    H2O_m    : wt% (dissolved water in melt)
    rho      : ohm-m
    sigma    : S/m
    eps_h/phic, eps_m/phim, eps_f/phig : crystal, melt, volatile fractions (0-1)
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Callable
import numpy as np
from scipy.special import erfc
from scipy import optimize

try:
    from skimage import measure as _skimage_measure

    _HAVE_SKIMAGE = True
except ImportError:
    _HAVE_SKIMAGE = False


# ---------------------------------------------------------------------------
# fugacity_PitzerSterner.py (Tony Withers, after Pitzer & Sterner 1994)
# -> PS_volume() / PS_fugacity()
#
# Direct translation of the module the original MATLAB Keppler.m called via
# py.importlib. Since we're already in Python, Keppler() below calls
# PS_volume() natively instead of bridging through MATLAB.
# ---------------------------------------------------------------------------

_PS_COEFF = [
    [0, 0, 0.24657688e6, 0.51359951e2, 0, 0],
    [0, 0, 0.58638965e0, -0.28646939e-2, 0.31375577e-4, 0],
    [0, 0, -0.62783840e1, 0.14791599e-1, 0.35779579e-3, 0.15432925e-7],
    [0, 0, 0, -0.42719875e0, -0.16325155e-4, 0],
    [0, 0, 0.56654978e4, -0.16580167e2, 0.76560762e-1, 0],
    [0, 0, 0, 0.10917883e0, 0, 0],
    [0.38878656e13, -0.13494878e9, 0.30916564e6, 0.75591105e1, 0, 0],
    [0, 0, -0.65537898e5, 0.18810675e3, 0, 0],
    [-0.14182435e14, 0.18165390e9, -0.19769068e6, -0.23530318e2, 0, 0],
    [0, 0, 0.92093375e5, 0.12246777e3, 0, 0],
]


def _PS_eos(volume: float, temperature: float, target_pressure: float) -> float:
    """
    Pitzer & Sterner (1994) equation of state, root-finding residual.
    volume : cc/mol
    temperature : Kelvin
    target_pressure : bars
    Returns (computed_pressure - target_pressure), bars.
    """
    R = 8314510.0  # Pa.cc/K/mol
    den = 1.0 / volume  # mol/cc

    c = [
        _PS_COEFF[i][0] * temperature**-4
        + _PS_COEFF[i][1] * temperature**-2
        + _PS_COEFF[i][2] * temperature**-1
        + _PS_COEFF[i][3]
        + _PS_COEFF[i][4] * temperature
        + _PS_COEFF[i][5] * temperature**2
        for i in range(10)
    ]

    pressure = (
        (
            den
            + c[0] * den**2
            - den**2
            * (
                (c[2] + 2 * c[3] * den + 3 * c[4] * den**2 + 4 * c[5] * den**3)
                / (c[1] + c[2] * den + c[3] * den**2 + c[4] * den**3 + c[5] * den**4)
                ** 2
            )
            + c[6] * den**2 * np.exp(-c[7] * den)
            + c[8] * den**2 * np.exp(-c[9] * den)
        )
        * R
        * temperature
        / 1e5
    )

    return pressure - target_pressure  # bars


def PS_volume(pressure: float, temperature: float) -> float:
    """
    H2O molar volume from the Pitzer & Sterner (1994) EOS.
    pressure : bars
    temperature : Kelvin
    Returns volume in cc/mol.
    """
    sol = optimize.root(_PS_eos, 10.0, args=(temperature, pressure))
    return float(sol.x[0])


def PS_fugacity(pressure: float, temperature: float) -> float:
    """
    H2O fugacity from the Pitzer & Sterner (1994) EOS.
    pressure : bars
    temperature : Kelvin
    Returns fugacity in bars. (Not used by Keppler(), included for
    completeness since it was part of the original module.)
    """
    R = 8314510.0
    c = [
        _PS_COEFF[i][0] * temperature**-4
        + _PS_COEFF[i][1] * temperature**-2
        + _PS_COEFF[i][2] * temperature**-1
        + _PS_COEFF[i][3]
        + _PS_COEFF[i][4] * temperature
        + _PS_COEFF[i][5] * temperature**2
        for i in range(10)
    ]
    volume = PS_volume(pressure, temperature)
    den = 1.0 / volume

    fug = (
        np.exp(
            np.log(den)
            + c[0] * den
            + (
                1 / (c[1] + c[2] * den + c[3] * den**2 + c[4] * den**3 + c[5] * den**4)
                - 1 / c[1]
            )
            - c[6] / c[7] * (np.exp(-c[7] * den) - 1)
            - c[8] / c[9] * (np.exp(-c[9] * den) - 1)
            + pressure * 1e5 / (den * R * temperature)
            + np.log(R * temperature)
            - 1
        )
        / 1e5
    )

    return float(fug)


# ---------------------------------------------------------------------------
# volfrac.m -> volfrac()
# ---------------------------------------------------------------------------


def volfrac(P: float, T: float, H2O_sys: float):
    """
    Direct port of volfrac.m.

    Computes crystal, melt, and volatile(gas) volume fractions, plus the
    dissolved water content in the melt, as a function of pressure (MPa),
    temperature (C), and total system water content (wt%).

    Returns
    -------
    eps_x : float   crystal fraction, 0-1
    eps_m : float   melt fraction, 0-1
    eps_g : float   exsolved volatile (gas) fraction, 0-1
    H2O_m : float   dissolved H2O in the melt, wt%
    """
    rho_x = 2900.0  # density of bulk crystal load, kg/m3
    rho_m = 2400.0  # density of melt, kg/m3

    # Volume ratio melt/(melt+crystals)
    A = -0.01006 * erfc(-0.7464 * (H2O_sys - 2.841)) - 0.00639
    B = 250.4 * np.exp(-0.9687 * H2O_sys) + 726.7 * np.exp(0.003698 * H2O_sys)
    r_melt = 0.5 * erfc(A * (T - B))

    # Maximum water solubility (Liu et al. 2005)
    H2O_sat = (354.94 * P**0.5 + 9.623 * P - 1.5223 * P**1.5) / (
        T + 273.15
    ) + 0.0012439 * P**1.5

    if r_melt == 0:
        H2O_hyp = H2O_sys  # hypothetical melt water content if all water is in melt
    else:
        H2O_hyp = H2O_sys * (r_melt * rho_m + (1 - r_melt) * rho_x) / (r_melt * rho_m)

    # EOS water density
    rho_g = (
        -112.528 * T**-0.381
        + 127.811 * (P * 10) ** -1.135
        + 112.04 * T**-0.411 * (P * 10) ** 0.033
    ) * 1e3

    # initial estimate (no gas)
    eps_m = r_melt
    eps_x = 1 - r_melt

    if H2O_hyp >= H2O_sat:
        H2O_m = H2O_sat
        eps_g_guess = 0.0001
        eps_x = r_melt * (eps_g_guess - 1) + 1 - eps_g_guess
        eps_m = 1 - eps_g_guess - eps_x
        rho_sys = eps_m * rho_m + eps_x * rho_x + eps_g_guess * rho_g
        H2O_total_est = (
            eps_g_guess * rho_g / rho_sys + eps_m * H2O_m / 100 * rho_m / rho_sys
        )

        while H2O_total_est < H2O_sys / 100:
            eps_g_guess += 0.0001
            eps_x = r_melt * (eps_g_guess - 1) + 1 - eps_g_guess
            eps_m = 1 - eps_g_guess - eps_x
            rho_sys = eps_m * rho_m + eps_x * rho_x + eps_g_guess * rho_g
            H2O_total_est = (
                eps_g_guess * rho_g / rho_sys + eps_m * H2O_m / 100 * rho_m / rho_sys
            )

        eps_g = eps_g_guess
    else:
        H2O_m = H2O_hyp
        eps_g = 0.0

    eps_x = r_melt * (eps_g - 1) + 1 - eps_g
    eps_m = 1 - eps_g - eps_x

    if eps_m < 1e-3:
        H2O_m = 0.0

    return eps_x, eps_m, eps_g, H2O_m


# ---------------------------------------------------------------------------
# melt_rho.m -> melt_rho()
# ---------------------------------------------------------------------------


def melt_rho(P: float, T: float, w: float, flag: int = 1) -> float:
    """
    Direct port of melt_rho.m -- melt electrical CONDUCTIVITY (S/m) from
    one of several published parameterizations, selected by `flag`:

        1 = RHYOLITE,  Guo et al. (2016)
        2 = DACITE,    Laumonier et al. (2015)
        3 = ANDESITE,  Laumonier et al. (2017)
        4 = ANDESITE,  Guo et al. (2017)
        5 = RHYOLITE,  Gaillard (2004)
        6 = BASALT,    Ni et al. (2011)
        7 = DACITE,    Laumonier et al. (2019)

    P : pressure, MPa
    T : temperature, C
    w : dissolved water content, wt%

    Returns sigma_melt in S/m. (In MELTS_MT_Rho.m this is inverted to get
    rhom = 1/melt_rho(...).)
    """
    if flag == 1:  # RHYOLITE, Guo et al. (2016)
        sigf = 10 ** (
            2.983
            - 0.0732 * w
            - (3528 - 233.8 * w + (0.763 - 0.0075 * w**2) * P) / (T + 273)
        )

    elif flag == 2:  # DACITE, Laumonier et al. (2015)
        dv = -0.176 * w - 0.388
        Ea = 6146 * w - 88400
        s1 = (-0.064 * w + 5.96) + P * 10 * (0.0000106 * w + 0.0000249)
        sigf = np.exp(s1 + (Ea + P * 10 * dv) / (8.314 * (T + 273)))

    elif flag == 3:  # ANDESITE, Laumonier et al. (2017)
        s1 = np.exp((-0.34 * w + 8.96) + P * 10 * (-0.00000807 * w + 0.000167))
        Ea = -9627 * w + 125000
        dv = -0.146 * w + 2.462
        sigf = s1 * np.exp(-((Ea + P * 10 * dv) / (8.314 * (T + 273))))

    elif flag == 4:  # ANDESITE, Guo et al. (2017)
        sigf = 10 ** (
            5.23
            - 0.56 * w**0.6
            - (8130.4 - 1462.7 * w**0.6 + (581.3 - 12.7 * w**2) * (P / 1000))
            / (T + 273)
        )

    elif flag == 5:  # RHYOLITE, Gaillard (2004)
        a = -78.9 * np.log(w) + 754
        b = -2925 * np.log(w) + 64132
        sigf = a * np.exp((-b + 2 * P) / (8.3144621 * (T + 273)))

    elif flag == 6:  # BASALT, Ni et al. (2011)
        sigf = 10 ** (2.172 - (860.82 - 204.46 * np.sqrt(w)) / (T + 273 - 1146.8))

    elif flag == 7:  # DACITE, Laumonier et al. (2019)
        a = 0.3947
        b = 4.648
        c = -1.772e-6
        d = 3.905e-5
        e = -8.215e-8
        f = 5.997e4
        g = 6.614e-11
        h = 0.6537
        R = 8.3144621
        sigf = np.exp(
            ((a * w + b) + P * 10 * (c * w + d))
            - (1 / (R * (T + 273)) * ((e * w + f) + P * 10 * (g * w + h)))
        )

    else:
        raise ValueError(f"Unknown flag={flag}. Must be 1-7. See docstring.")

    return float(sigf)


# ---------------------------------------------------------------------------
# Keppler.m -> Keppler()
# ---------------------------------------------------------------------------


def Keppler(P: float, T: float, con: float, flag: int = 1) -> float:
    """
    Direct port of Keppler.m -- aqueous volatile/brine phase electrical
    CONDUCTIVITY (S/m), using one of three empirical relations from
    Hans Keppler's research group, selected by `flag`:

        1 = Sinmyo & Keppler (2017): NaCl-bearing fluids, to 1000 MPa,
            600 C (figures extrapolate 250-1400 C)
        2 = Guo & Keppler (2019): NaCl-bearing fluids, to 5000 MPa,
            900 C (figures span 1000-5000 MPa, 300-900 C)
        3 = Klumbach & Keppler (2020): HCl-bearing fluids, to 1000 GPa,
            700 C (figures extrapolate to 100 MPa, 150-800 C)

    Per Hans Keppler (pers. comm. per the original docstring), flag 1 or 3
    are preferred for volcanic environments; lower pressures are valid.

    P   : pressure, MPa
    T   : temperature, C
    con : concentration, wt% (NaCl-equivalent for flags 1-2, HCl-equivalent
          for flag 3)
    flag: 1, 2, or 3 -- selects the empirical relation

    Returns sigma_fluid in S/m.

    Internally uses the Pitzer & Sterner (1994) H2O equation of state
    (PS_volume, above) to get H2O density at P, T -- this replaces the
    original MATLAB's py.importlib bridge into fugacity_PitzerSterner.py,
    since we're calling it natively here instead.
    """
    molar_mass = 18.02  # g/mol, H2O

    molar_concentration_NaCl = (con * 10) / 58.44  # mol/L
    molar_concentration_HCl = (con * 10) / 36.458  # mol/L
    c_hcl = con * (
        molar_concentration_HCl / molar_concentration_NaCl
    )  # NaCl-equiv HCl conc.

    # PS_volume expects P in bars, T in Kelvin
    cc_per_mol = PS_volume(P * 10, T + 273)
    rho = molar_mass * (1.0 / cc_per_mol)  # g/cc

    TK = T + 273

    if flag == 1:
        # Sinmyo & Keppler (2017)
        lambda0 = 1573 - 1212 * rho + 537062 / TK - 208122721 / TK**2
        sigf = 10 ** (
            -1.7060
            - 93.78 / TK
            + 3.0781 * np.log10(rho)
            + 0.8075 * np.log10(con)
            + np.log10(lambda0)
        )

    elif flag == 2:
        # Guo & Keppler (2019)
        lambda0 = 1573 - 1212 * rho + 537062 / TK - 208122721 / TK**2
        sigf = 10 ** (
            -0.919
            - 872.5 / TK
            + 7.61 * np.log10(rho)
            + 0.852 * np.log10(con)
            + np.log10(lambda0)
        )

    elif flag == 3:
        # Klumbach & Keppler (2020)
        lambda0 = 2550.14 - 505.1 * rho - 429437 / TK
        sigf = 10 ** (
            -2.032
            + 205.8 / TK
            + 3.888 * np.log10(rho)
            + 0.895 * np.log10(c_hcl)
            + np.log10(lambda0)
        )

    else:
        raise ValueError(f"Unknown flag={flag}. Must be 1, 2, or 3. See docstring.")

    return float(sigf)


# ---------------------------------------------------------------------------
# Hashim et al. (2013) crystal resistivity -- exact, verbatim translation
# ---------------------------------------------------------------------------


def hashim_crystal_resistivity(T_celsius: float) -> float:
    """
    rhoh = exp(-log(2.9) + 8581.8 / (T + 273))
    T_celsius in C. Returns resistivity in ohm-m.
    """
    return float(np.exp(-np.log(2.9) + 8581.8 / (T_celsius + 273.0)))


# ---------------------------------------------------------------------------
# MAL3.m -> MAL3()  (3-phase Modified Archie's Law, Glover 2010)
# ---------------------------------------------------------------------------


def MAL3(
    sigc: float,
    sigm: float,
    sigg: float,
    phic: float,
    phim: float,
    phig: float,
    mm: float,
    mg: float,
) -> float:
    """
    Direct port of MAL3.m -- 3-phase Modified Archie's Law (Glover, 2010).

    sigc, sigm, sigg : crystal, melt, volatile conductivities (S/m)
    phic, phim, phig : crystal, melt, volatile volume fractions (0-1)
    mm, mg           : melt and volatile connectivity exponents

    Returns bulk conductivity, S/m.
    """
    if phic == 0:
        phic = 1e-4

    Gm = phim**mm
    Gg = phig**mg

    mc = np.log(1 - Gg - Gm) / np.log(phic)
    Gc = phic**mc

    Gchecksum = Gc + Gm + Gg

    sig = sigc * Gc + sigm * Gm + sigg * Gg

    if abs(Gchecksum - 1) > 1e-3:
        raise ValueError("G not equal 1. Something wrong.")

    sig_complex = complex(sig)
    if abs(sig_complex.imag) > 1e-3:
        raise ValueError("Imaginary conductivities. Something wrong.")
    else:
        sig = sig_complex.real

    return float(sig)


# ---------------------------------------------------------------------------
# MAL.m -> MAL()  (2-phase Modified Archie's Law, Glover et al. 2000)
# ---------------------------------------------------------------------------


def MAL(sigm: float, sigf: float, m: float, phi: float) -> float:
    """
    Direct port of MAL.m -- 2-phase Modified Archie's Law (Glover et al. 2000).

    phi  : volume fraction of the MORE conductive material
    sigm : matrix (less conductive) conductivity
    sigf : fluid (more conductive) conductivity
    m    : connectivity parameter

    Note: mirrors the MATLAB behavior exactly, including that if
    sigf <= sigm it swaps by setting sigf = sigm and prints a warning
    rather than raising -- this matches the original's (slightly unusual)
    error-handling choice.
    """
    if sigf <= sigm:
        sigf = sigm
        print(
            "The volume fraction must be associated with the more conductive "
            "material. Try (1-phi) instead"
        )

    if phi == 1:
        return float(sigf)

    p = np.log10(1 - phi**m) / np.log10(1 - phi)
    sig = sigf * phi**m + sigm * (1 - phi) ** p
    return float(sig)


def MAL_solve_phi(rho_b, rho_h, rho_f, m):
    """
    Direct port of MAL_solve_phi.m -- inverse of MAL(): solves for melt
    fraction (phi) given bulk, host, and fluid resistivities and a
    connectivity exponent m.

    Vectorized: rho_b, rho_h, rho_f can be scalars or numpy arrays.
    Returns phi (NaN where inputs violate ordering constraints
    rho_f <= rho_b <= rho_h).
    """
    rho_b = np.asarray(rho_b, dtype=float)
    rho_h = np.asarray(rho_h, dtype=float)
    rho_f = np.asarray(rho_f, dtype=float)

    bad = (rho_b > rho_h) | (rho_b < rho_f) | (rho_f > rho_h)
    if np.any(rho_b > rho_h):
        print("Bulk resistivity cannot be greater than matrix resistivity")
    if np.any(rho_b < rho_f):
        print("Bulk resistivity cannot be less than fluid resistivity")
    if np.any(rho_f > rho_h):
        print("Fluid resistivity cannot be greater than matrix resistivity")

    sigb = 1.0 / rho_b
    sigf = 1.0 / rho_f
    sigh = 1.0 / rho_h

    phi = ((sigb - sigh) / (sigf - sigh)) ** (1.0 / m)
    phi = np.where(bad, np.nan, phi)

    return phi if phi.shape else float(phi)


# ---------------------------------------------------------------------------
# HS.m / HS_solve_phi.m -> HS() / HS_solve_phi()
# ---------------------------------------------------------------------------


def HS(sigm: float, sigf: float, phi: float):
    """
    Direct port of HS.m -- Hashin-Shtrikman upper and lower bounds.

    phi  : volume fraction of the more conductive material
    sigm : matrix conductivity
    sigf : fluid conductivity  (must be >= sigm; else raises, matching MATLAB)

    Returns (sigplus, sigminus) -- HS+ and HS- bounds.

    NOTE: translated verbatim from HS.m, including its formula for
    sigminus using (sigm + sigf) in a denominator term. This looks
    structurally asymmetric relative to the standard textbook HS- formula
    (which would mirror HS+ with phases swapped), but it is reproduced
    exactly as written in the source rather than "corrected," since I
    can't be sure whether this was a deliberate choice or a typo in the
    original without more context. Worth double-checking against Glover
    (2000) if you rely on sigminus specifically.
    """
    if sigf <= sigm:
        raise ValueError(
            "The volume fraction must be associated with the more conductive "
            "material. Try (1-phi) instead"
        )

    phi1 = phi
    phi2 = 1 - phi1

    sigplus = sigf + phi2 / ((1 / (sigm - sigf)) + (phi1 / (3 * sigf)))
    sigminus = sigm + phi1 / ((1 / (sigm + sigf)) + (phi2 / (3 * sigm)))

    return float(sigplus), float(sigminus)


def HS_solve_phi(rho_b: float, rho_h: float, rho_f: float):
    """
    Direct port of HS_solve_phi.m -- solves for melt fraction (phi) using
    HS+ given bulk, host, and fluid resistivities.

    Returns (phi, phi2) -- two algebraic forms, matching the MATLAB source
    (which keeps both, with the second as an alternate derivation / sanity
    check -- the original leaves commented-out intermediate forms too).
    """
    if rho_b > rho_h:
        print("Bulk resistivity cannot be greater than matrix resistivity")
    if rho_b < rho_f:
        print("Bulk resistivity cannot be less than fluid resistivity")
    if rho_f > rho_h:
        print("Fluid resistivity cannot be greater than matrix resistivity")

    sigf = 1.0 / rho_f
    sigm = 1.0 / rho_h
    sigb = 1.0 / rho_b

    phi = (3 * sigf * (sigm - sigb)) / (
        3 * sigf * (sigm - sigf + (1 / 3) * sigf)
        + sigm * sigb
        - sigf * sigm
        - sigb * sigf
    )

    phi2 = (sigm - sigb) / (
        (2 / 3) * (sigm - sigf) + (1 / 3) * sigb * (sigm / sigf - 1)
    )

    return float(phi), float(phi2)


# ---------------------------------------------------------------------------
# Results container (mirrors the MATLAB `results` struct)
# ---------------------------------------------------------------------------


@dataclass
class RhoResult:
    meltfrac: float
    volfrac: float
    xfrac: float
    meltH2O: float
    rhoh: float
    rhom: float
    rhof: float
    rhob: float


def _phases_to_bulk_resistivity(
    eps_h: float,
    eps_m: float,
    eps_g: float,
    H2O_m: float,
    P: float,
    T: float,
    c: float = 1.15,
    rhoh: Optional[float] = None,
    volflag: bool = False,
    concentration: float = 1.0,
    cf: float = 3.0,
    melt_flag: int = 1,
) -> RhoResult:
    """
    Shared core: given ALREADY-KNOWN phase fractions (crystal/melt/volatile)
    and dissolved melt water, compute phase resistivities and combine them
    via 3-phase MAL3 into a bulk resistivity.

    This is factored out of melts_mt_rho() so the same downstream physics
    (melt_rho, Keppler, MAL3) can be driven either by:
        - the empirical volfrac() parameterization (see melts_mt_rho), or
        - real phase fractions read from actual alphaMELTS output
          (see AlphaMeltsRun.compute_resistivity_profile)

    eps_h, eps_m, eps_g : crystal, melt, volatile fractions (0-1, sum to 1)
    H2O_m : dissolved water in the melt, wt%
    P : pressure, MPa
    T : temperature, C
    (other params as in melts_mt_rho)
    """
    if eps_g > 0 and not volflag:
        print("Warning: Melt is saturated but you are ignoring the volatiles!")
        rhom = np.nan
        rhof = np.nan
        rhob = np.nan
        rhoh_out = rhoh if rhoh else 0.0
    else:
        sigma_melt = melt_rho(P, T, H2O_m, melt_flag)
        rhom = 1.0 / sigma_melt

        sigma_fluid = Keppler(P, T, concentration, 1)
        rhof = 1.0 / sigma_fluid

        if rhoh is None or rhoh == 0:
            rhoh_out = hashim_crystal_resistivity(T)
        else:
            rhoh_out = rhoh

        sigma_bulk = MAL3(
            1.0 / rhoh_out, 1.0 / rhom, 1.0 / rhof, eps_h, eps_m, eps_g, c, cf
        )
        rhob = 1.0 / sigma_bulk

    return RhoResult(
        meltfrac=eps_m,
        volfrac=eps_g,
        xfrac=eps_h,
        meltH2O=H2O_m,
        rhoh=rhoh_out,
        rhom=rhom,
        rhof=rhof,
        rhob=rhob,
    )


# ---------------------------------------------------------------------------
# MELTS_MT_Rho.m -> melts_mt_rho()
# ---------------------------------------------------------------------------


def melts_mt_rho(
    H2O_sys: float,
    T: float,
    P: float,
    c: float = 1.15,
    rhoh: Optional[float] = None,
    volflag: bool = False,
    concentration: float = 1.0,
    cf: float = 3.0,
    melt_flag: int = 1,
) -> RhoResult:
    """
    Direct port of MELTS_MT_Rho.m.

    Uses the empirical volfrac() parameterization (an erfc-based fit to a
    single pre-computed MELTS bulk composition) to get phase fractions,
    then calls _phases_to_bulk_resistivity() for the resistivity physics.

    H2O_sys : total system water content, wt%
    T       : temperature, C
    P       : pressure, MPa
    c       : melt connectivity parameter for MAL3 (MATLAB default = 1.15)
    rhoh    : fixed crystal resistivity, ohm-m. None -> Hashim et al. (2013) default.
    volflag : calculate in saturated/volatile-present regime (default False)
    concentration : NaCl-equivalent wt% for volatile phase (default 1 wt%)
    cf      : volatile connectivity parameter for MAL3 (default 3.0)
    melt_flag : which melt_rho() composition/parameterization to use
                (default 1 = rhyolite, Guo et al. 2016)
    """
    eps_h, eps_m, eps_f, H2O_m = volfrac(P, T, H2O_sys)
    return _phases_to_bulk_resistivity(
        eps_h, eps_m, eps_f, H2O_m, P, T, c, rhoh, volflag, concentration, cf, melt_flag
    )


# ---------------------------------------------------------------------------
# MELTS_MT_MagmaRes.m -> melts_mt_magma_res()
# ---------------------------------------------------------------------------


def melts_mt_magma_res(
    rhob_fixed: float,
    H2O_sys: np.ndarray,
    T: np.ndarray,
    P: np.ndarray,
    c: float = 1.15,
    rhoh: Optional[float] = None,
    volflag: bool = False,
    concentration: float = 1.0,
    cf: float = 3.0,
    melt_flag: int = 1,
    confirm_large_run: Optional[Callable[[int], bool]] = None,
):
    """
    Direct port of MELTS_MT_MagmaRes.m.

    Grids T x H2O_sys at each pressure in P, computes bulk resistivity at
    every point, then extracts the contour where bulk resistivity equals
    rhob_fixed (equivalent to MATLAB's contourc).

    Returns a dict keyed by pressure index k (0-based); each value is an
    (N, 6) array with columns:
        [H2O_sys_on_contour, T_on_contour, meltfrac, volfrac, meltH2O, rhob]

    Requires scikit-image (`pip install scikit-image`).
    """
    if not _HAVE_SKIMAGE:
        raise ImportError(
            "melts_mt_magma_res() requires scikit-image for contour "
            "extraction (equivalent to MATLAB's contourc). "
            "Install with: pip install scikit-image"
        )

    H2O_sys = np.asarray(H2O_sys, dtype=float)
    T = np.asarray(T, dtype=float)
    P = np.asarray(P, dtype=float)

    total_calc = len(H2O_sys) * len(T) * len(P)
    if total_calc > 1e4:
        proceed = confirm_large_run(total_calc) if confirm_large_run else True
        if not proceed:
            return None

    n_T, n_H2O, n_P = len(T), len(H2O_sys), len(P)
    rhob_arr = np.full((n_T, n_H2O, n_P), np.nan)

    for i, T_i in enumerate(T):
        for j, H2O_j in enumerate(H2O_sys):
            for k, P_k in enumerate(P):
                res = melts_mt_rho(
                    H2O_j, T_i, P_k, c, rhoh, volflag, concentration, cf, melt_flag
                )
                rhob_arr[i, j, k] = res.rhob
        print(f"T = {T_i} C: Complete")

    magma_res = {}
    for k in range(n_P):
        grid = rhob_arr[:, :, k]
        contours_idx = _skimage_measure.find_contours(grid, level=rhob_fixed)

        rows = []
        for contour in contours_idx:
            for row_idx, col_idx in contour:
                T_val = np.interp(row_idx, np.arange(n_T), T)
                H2O_val = np.interp(col_idx, np.arange(n_H2O), H2O_sys)
                res = melts_mt_rho(
                    H2O_val, T_val, P[k], c, rhoh, volflag, concentration, cf, melt_flag
                )
                rows.append(
                    [H2O_val, T_val, res.meltfrac, res.volfrac, res.meltH2O, res.rhob]
                )

        magma_res[k] = np.array(rows) if rows else np.empty((0, 6))

    return magma_res


# ---------------------------------------------------------------------------
# AlphaMeltsRun -- link real alphaMELTS output into the resistivity pipeline
# ---------------------------------------------------------------------------


@dataclass
class AlphaMeltsStep:
    """One step (one P-T point) from a parsed alphaMELTS run."""

    T_C: float
    P_MPa: float
    eps_h: float  # crystal (solid) fraction, 0-1
    eps_m: float  # melt fraction, 0-1
    eps_g: float = 0.0  # exsolved volatile/fluid fraction, 0-1
    H2O_melt: float = 0.0  # dissolved H2O in melt, wt%
    melt_composition: Optional[dict] = None  # e.g. {"SiO2": 75.1, "MgO": 0.3, ...}


class AlphaMeltsRun:
    """
    Container for a parsed alphaMELTS run, linking real thermodynamic
    output into the MELTS_MT resistivity pipeline -- as an alternative to
    the empirical volfrac() parameterization (which is fixed to a single
    pre-calibrated bulk composition and cannot see compositional changes
    like MgO content).

    Using this class means: phase fractions (crystal/melt/volatile) and
    dissolved melt water come directly from your actual alphaMELTS run,
    not from the erfc-fit. The resistivity PHYSICS (melt_rho, Keppler,
    MAL3) is unchanged and still only consumes P, T, and dissolved H2O for
    melt conductivity -- so this does NOT, by itself, make melt_rho
    "composition-aware." It removes the volfrac bottleneck on melt
    fraction/H2O partitioning, but a compositionally-sensitive conductivity
    law (e.g. one with an explicit MgO or alkali term) would need to be
    supplied separately -- see `custom_melt_conductivity_fn` below.

    IMPORTANT -- alphaMELTS output format caveat:
    alphaMELTS/rhyolite-MELTS output table structure and column headers
    vary by version and run mode (isobaric/isothermal/polybaric;
    Phase_main_tbl.txt vs separate per-phase tables, etc.). The parser
    below is deliberately built around an explicit, overridable column
    mapping rather than hard-coded header names, since I can't verify the
    exact format without seeing a real output file from your version. If
    parsing fails or silently grabs the wrong columns, paste a short
    sample (even just the header row + 2-3 data rows) and I'll tighten
    the mapping to match exactly.
    """

    def __init__(self, steps: list):
        self.steps = steps

    @classmethod
    def from_dataframe(
        cls,
        df,
        column_map: Optional[dict] = None,
        temperature_units: str = "C",
        pressure_units: str = "bar",
        mass_basis: str = "fraction",
    ) -> "AlphaMeltsRun":
        """
        Build an AlphaMeltsRun from an already-loaded pandas DataFrame
        (e.g. from pd.read_csv on a Phase_main_tbl.txt-style file, or from
        a Python wrapper around the alphaMELTS C library).

        Parameters
        ----------
        df : pandas.DataFrame
            One row per P-T step.
        column_map : dict, optional
            Maps this module's required fields to YOUR dataframe's actual
            column names. Required keys and their meaning:
                "T"        -> temperature column
                "P"        -> pressure column
                "melt_mass_frac"  -> melt mass or mass-fraction column
                "solid_mass_frac" -> crystal mass or mass-fraction column
                "fluid_mass_frac" -> exsolved fluid mass/fraction column
                                     (optional; assumed 0 if absent)
                "H2O_melt" -> dissolved H2O in melt, wt% (liquid composition)
            Optionally, oxide columns for melt composition, e.g.:
                "SiO2", "TiO2", "Al2O3", "FeO", "Fe2O3", "MgO", "CaO",
                "Na2O", "K2O"
            If None, this method assumes df's columns are ALREADY named
            exactly as above (unlikely for raw alphaMELTS output -- you
            will almost certainly need to supply this).
        temperature_units : "C" or "K" -- units of the T column in df
        pressure_units : "bar", "MPa", or "GPa" -- units of the P column in df
        mass_basis : "fraction" if melt/solid/fluid columns already sum to
            1 (or ~1), or "mass" if they're absolute masses that need to be
            normalized by their row sum (common in raw alphaMELTS phase
            tables, which report mass in grams per 100g system or similar).

        Returns
        -------
        AlphaMeltsRun
        """
        default_map = {
            "T": "T",
            "P": "P",
            "melt_mass_frac": "melt_mass_frac",
            "solid_mass_frac": "solid_mass_frac",
            "fluid_mass_frac": "fluid_mass_frac",
            "H2O_melt": "H2O_melt",
        }
        cmap = {**default_map, **(column_map or {})}

        required = ["T", "P", "melt_mass_frac", "solid_mass_frac"]
        missing = [k for k in required if cmap[k] not in df.columns]
        if missing:
            raise ValueError(
                f"Required columns not found in dataframe: "
                f"{[cmap[k] for k in missing]}\n"
                f"Available columns: {list(df.columns)}\n"
                f"Pass an explicit column_map= to AlphaMeltsRun.from_dataframe() "
                f"mapping required fields to your actual column names, e.g.:\n"
                f'  column_map={{"T": "Temperature(C)", "P": "Pressure(bars)", '
                f'"melt_mass_frac": "liquid_0 mass", ...}}'
            )

        oxide_names = [
            "SiO2",
            "TiO2",
            "Al2O3",
            "FeO",
            "Fe2O3",
            "MgO",
            "CaO",
            "Na2O",
            "K2O",
        ]
        oxide_cols = {
            ox: cmap.get(ox, ox) for ox in oxide_names if cmap.get(ox, ox) in df.columns
        }

        steps = []
        for _, row in df.iterrows():
            T_val = float(row[cmap["T"]])
            T_C = T_val - 273.15 if temperature_units.upper() == "K" else T_val

            P_val = float(row[cmap["P"]])
            if pressure_units.lower() == "bar":
                P_MPa = P_val / 10.0
            elif pressure_units.lower() == "gpa":
                P_MPa = P_val * 1000.0
            else:  # already MPa
                P_MPa = P_val

            melt_raw = float(row[cmap["melt_mass_frac"]])
            solid_raw = float(row[cmap["solid_mass_frac"]])
            fluid_col = cmap.get("fluid_mass_frac")
            fluid_raw = (
                float(row[fluid_col]) if fluid_col and fluid_col in df.columns else 0.0
            )

            if mass_basis == "mass":
                total = melt_raw + solid_raw + fluid_raw
                eps_m = melt_raw / total if total > 0 else 0.0
                eps_h = solid_raw / total if total > 0 else 0.0
                eps_g = fluid_raw / total if total > 0 else 0.0
            else:
                eps_m, eps_h, eps_g = melt_raw, solid_raw, fluid_raw

            H2O_melt_col = cmap.get("H2O_melt")
            H2O_melt = float(row[H2O_melt_col]) if H2O_melt_col in df.columns else 0.0

            melt_comp = (
                {ox: float(row[col]) for ox, col in oxide_cols.items()}
                if oxide_cols
                else None
            )

            steps.append(
                AlphaMeltsStep(
                    T_C=T_C,
                    P_MPa=P_MPa,
                    eps_h=eps_h,
                    eps_m=eps_m,
                    eps_g=eps_g,
                    H2O_melt=H2O_melt,
                    melt_composition=melt_comp,
                )
            )

        return cls(steps)

    @classmethod
    def from_file(
        cls,
        path: str,
        column_map: Optional[dict] = None,
        temperature_units: str = "C",
        pressure_units: str = "bar",
        mass_basis: str = "fraction",
        sep: str = r"\s+",
        **read_csv_kwargs,
    ) -> "AlphaMeltsRun":
        """
        Convenience wrapper: read a whitespace- or comma-delimited
        alphaMELTS output file into a DataFrame, then call from_dataframe().

        For alphaMELTS 1.x Phase_main_tbl.txt-style files, the default
        whitespace separator usually works, but you may need to adjust
        `sep` (e.g. sep="," for CSV exports) or skip header/comment rows
        via `read_csv_kwargs` (e.g. skiprows=3, comment="!").

        See from_dataframe() for column_map / units documentation.
        """
        import pandas as pd

        df = pd.read_csv(path, sep=sep, engine="python", **read_csv_kwargs)
        df.columns = [c.strip() for c in df.columns]
        return cls.from_dataframe(
            df,
            column_map=column_map,
            temperature_units=temperature_units,
            pressure_units=pressure_units,
            mass_basis=mass_basis,
        )

    def compute_resistivity_profile(
        self,
        c: float = 1.15,
        rhoh: Optional[float] = None,
        volflag: bool = True,
        concentration: float = 1.0,
        cf: float = 3.0,
        melt_flag: int = 1,
        custom_melt_conductivity_fn: Optional[
            Callable[["AlphaMeltsStep"], float]
        ] = None,
    ):
        """
        Run every step through the resistivity physics (melt_rho, Keppler,
        MAL3), using REAL phase fractions and dissolved water from the
        parsed alphaMELTS run instead of the empirical volfrac() fit.

        volflag defaults to True here (unlike melts_mt_rho's default of
        False) because real alphaMELTS output will often include a
        genuine nonzero fluid phase at points in the run, and silently
        returning NaN at every such step would likely discard most of a
        real crystallization path. Set volflag=False if you specifically
        want to reproduce the original MATLAB's stricter behavior.

        custom_melt_conductivity_fn : optional callable(AlphaMeltsStep) ->
            sigma_melt (S/m). If provided, this REPLACES the call to
            melt_rho() for the melt phase -- this is the hook for plugging
            in a compositionally-sensitive conductivity law (e.g. one with
            an explicit MgO, alkali, or Fe term) using the
            `melt_composition` dict on each step, since none of the
            published melt_rho() laws in this module take composition
            beyond dissolved H2O. Supplying this is on you / requires a
            literature source for such a law -- I won't fabricate one.

        Returns
        -------
        list[RhoResult], one per step, in the same order as self.steps.
        """
        results = []
        for step in self.steps:
            if custom_melt_conductivity_fn is not None:
                # Manually replicate _phases_to_bulk_resistivity but with a
                # substituted melt conductivity source.
                if step.eps_g > 0 and not volflag:
                    print(
                        "Warning: Melt is saturated but you are ignoring the volatiles!"
                    )
                    results.append(
                        RhoResult(
                            meltfrac=step.eps_m,
                            volfrac=step.eps_g,
                            xfrac=step.eps_h,
                            meltH2O=step.H2O_melt,
                            rhoh=rhoh or 0.0,
                            rhom=np.nan,
                            rhof=np.nan,
                            rhob=np.nan,
                        )
                    )
                    continue

                sigma_melt = custom_melt_conductivity_fn(step)
                rhom = 1.0 / sigma_melt
                sigma_fluid = Keppler(step.P_MPa, step.T_C, concentration, 1)
                rhof = 1.0 / sigma_fluid
                rhoh_out = (
                    hashim_crystal_resistivity(step.T_C)
                    if (rhoh is None or rhoh == 0)
                    else rhoh
                )
                sigma_bulk = MAL3(
                    1.0 / rhoh_out,
                    1.0 / rhom,
                    1.0 / rhof,
                    step.eps_h,
                    step.eps_m,
                    step.eps_g,
                    c,
                    cf,
                )
                rhob = 1.0 / sigma_bulk
                results.append(
                    RhoResult(
                        meltfrac=step.eps_m,
                        volfrac=step.eps_g,
                        xfrac=step.eps_h,
                        meltH2O=step.H2O_melt,
                        rhoh=rhoh_out,
                        rhom=rhom,
                        rhof=rhof,
                        rhob=rhob,
                    )
                )
            else:
                results.append(
                    _phases_to_bulk_resistivity(
                        step.eps_h,
                        step.eps_m,
                        step.eps_g,
                        step.H2O_melt,
                        step.P_MPa,
                        step.T_C,
                        c,
                        rhoh,
                        volflag,
                        concentration,
                        cf,
                        melt_flag,
                    )
                )

        return results

    def to_dataframe(
        self,
        c: float = 1.15,
        rhoh: Optional[float] = None,
        volflag: bool = True,
        concentration: float = 1.0,
        cf: float = 3.0,
        melt_flag: int = 1,
        custom_melt_conductivity_fn=None,
    ):
        """
        Convenience: compute_resistivity_profile() plus the original T/P/
        composition, assembled into a pandas DataFrame for easy plotting
        or export.
        """
        import pandas as pd

        results = self.compute_resistivity_profile(
            c, rhoh, volflag, concentration, cf, melt_flag, custom_melt_conductivity_fn
        )
        rows = []
        for step, res in zip(self.steps, results):
            row = {
                "T_C": step.T_C,
                "P_MPa": step.P_MPa,
                "eps_h": res.xfrac,
                "eps_m": res.meltfrac,
                "eps_g": res.volfrac,
                "H2O_melt": res.meltH2O,
                "rhoh": res.rhoh,
                "rhom": res.rhom,
                "rhof": res.rhof,
                "rhob": res.rhob,
            }
            if step.melt_composition:
                row.update(step.melt_composition)
            rows.append(row)
        return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Example usage
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Full pipeline smoke test -- all dependencies now implemented
    result = melts_mt_rho(H2O_sys=4.0, T=800.0, P=150.0)
    print(result)

    # Rhyolite MgO-series style sanity check is NOT directly supported here,
    # since MgO is not a volfrac/melt_rho input in this parameterization --
    # see conversation above: this pipeline's melt conductivity laws key on
    # H2O content, T, and P only, consistent with Guo et al. (2016) etc.
    # not including an explicit MgO term.

    print("\nSweep over total system water content at fixed T, P:")
    for h2o in [1, 2, 3, 4, 5, 6]:
        r = melts_mt_rho(H2O_sys=h2o, T=800.0, P=150.0)
        print(
            f"  H2O_sys={h2o} wt%  meltfrac={r.meltfrac:.3f}  "
            f"meltH2O={r.meltH2O:.3f} wt%  rhob={r.rhob:.3e} ohm-m"
        )
