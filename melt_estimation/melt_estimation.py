from dataclasses import dataclass
from typing import Dict, Optional, Tuple
import numpy as np

# -----------------------------
# 1) Data containers (MELTS-like)
# -----------------------------


@dataclass
class MELTSState:
    """Container for alphaMELTS/rhyolite-MELTS outputs you care about."""

    temperature_K: float
    pressure_GPa: float
    melt_fraction: float  # Thermodynamic φ from MELTS (can be used as a prior)
    melt_composition: Dict[str, float]  # e.g., oxides wt% + H2O, CO2
    mineral_modes: Dict[str, float]  # e.g., {"olivine":0.55,"opx":0.25,...}
    melt_density_kg_m3: Optional[float] = None
    solid_density_kg_m3: Optional[float] = None


# ------------------------------------
# 2) Melt conductivity parameterization
# ------------------------------------


class MeltConductivityModel:
    """
    Compute melt conductivity σ_melt(T, composition) with an Arrhenius-type expression
    and simple volatile/redox corrections.

    σ_melt(T) = σ0 * exp( - (Ea - kH*X_H2O - kC*X_CO2 - kR*Δredox) / (R*T) )
    Units: S/m

    Literature indicates strong dependence of silicate melt conductivity on T, H2O, CO2 and redox.  # see README refs
    """

    R = 8.314  # J/mol/K

    def __init__(self, weight_percent_water=0, pressure=0.2, temperature=1275):
        self.weight_percent_water = weight_percent_water  # weight percent
        self.pressure = pressure  # pressure in GPa
        self.temperature = temperature  # temperature in Kelvin
        self.gas_constant = 8.31446261815324

    @property
    def intitial_sigma(self):
        # from Galliard2004
        return -78.9 * np.log(self.weight_percent_water) + 754

    @property
    def activation_energy(self):
        # from Galliard2004
        return -2925 * np.log(self.weight_percent_water) + 64132

    def compute(self, temperature=None, weight_percent_water=None) -> float:
        if temperature is not None:
            self.temperature = temperature
        if weight_percent_water is not None:
            self.weight_percent_water = weight_percent_water

        return self.intitial_sigma * np.exp(
            (-self.activation_energy + 2 * self.pressure)
            / (self.gas_constant * self.temperature)
        )

        # X_H2O = (comp.get("H2O", 0.0) or 0.0) / 100.0  # mass fraction if wt% provided
        # X_CO2 = (comp.get("CO2", 0.0) or 0.0) / 100.0
        # redox = comp.get("DeltaFMQ", 0.0)  # optional redox proxy
        # Ea_eff = self.Ea_J - self.kH_J*X_H2O - self.kC_J*X_CO2 - self.kR_J*redox
        # return float(self.sigma0_S * np.exp(-Ea_eff / (self.R * T_K)))


# ----------------------------------------------------
# 3) Electrical mixing: Modified Archie's law (melt φ)
# ----------------------------------------------------


class ModifiedArchieModel:
    """
    Bulk conductivity model for partially molten aggregate:

    For φ > φ_c:
      σ_bulk = σ_solid*(1-φ) + C * σ_melt * ((φ - φ_c)/(1 - φ_c))**n
    For φ ≤ φ_c:
      σ_bulk ≈ σ_solid*(1-φ)   (no percolation; melt disconnected)

    - C: connectivity/geometry factor
    - n: Archie exponent (∼1.0–2.0 for interconnected melts)
    - φ_c: percolation threshold (∼0–0.03 depending on texture)
    """

    def __init__(
        self,
        rock_conductivity=0.01,
        melt_conductivity=1,
        melt_percent=0.3,
        connnectivity_exponent=1.05,
    ):
        self.rock_conductivity = rock_conductivity
        self.melt_conductivity = melt_conductivity
        self.melt_percent = np.clip(melt_percent, 0.0, 0.999)
        self.connectivity_exponent = connnectivity_exponent

    def compute(self):
        """
        modified archies law

        sigma_1 is the resistivity of the host material
        sigma_2 is the resistivity of the filling material
        percent_2 is the percentage of the filling material
        """
        s1 = self.rock_conductivity
        s2 = self.melt_conductivity
        p2 = 1 - self.melt_percent

        p = np.log(1 - p2**self.connectivity_exponent) / np.log(1 - p2)

        sigma_eff = s1 * (1 - p2) ** p + s2 * p2**self.connectivity_exponent

        return sigma_eff


# ---------------------------------------------------------
# 4) Seismic baseline (solids) and melt sensitivity on Vp
# ---------------------------------------------------------


class ElasticAggregate:
    """
    Baseline elastic properties (no melt) from mineral modes.
    For now, provide (K, G, rho) directly; later wire MinVel for VRH at T,P.
    """

    def __init__(self, bulk_modulus: float, shear_modulus: float, rho_kg_m3: float):
        self.bulk_modulus = bulk_modulus * 1e9  # Bulk Modulus [Pa]
        self.shear_modulus = shear_modulus * 1e9  # Shear Modulus [Pa]
        self.density = rho_kg_m3  # Density [kg/m3]

    @property
    def vp_ms(self) -> float:
        return float(
            np.sqrt((self.bulk_modulus + 4.0 * self.shear_modulus / 3.0) / self.density)
        )

    @property
    def vs_ms(self) -> float:
        return float(np.sqrt(self.shear_modulus / self.density))


class SeismicMeltReduction:
    """
    First-order melt fraction sensitivity for Vp and Vs:

    Vp(φ) = Vp0 * (1 - a_vp * φ)
    Vs(φ) = Vs0 * (1 - a_vs * φ)
    """

    def __init__(self, a_vp=1.2, a_vs=2.0):
        self.a_vp = a_vp
        self.a_vs = a_vs

    def vp(self, vp0_ms: float, phi: float) -> float:
        return float(vp0_ms * (1.0 - self.a_vp * phi))

    def vs(self, vs0_ms: float, phi: float) -> float:
        return float(vs0_ms * (1.0 - self.a_vs * phi))


# ---------------------------------------
# Seismic Differential Effective Medium
# ---------------------------------------


# filename: src/seismic_dem.py
from dataclasses import dataclass
import numpy as np

# Optional external dependency: rockphypy (Berryman DEM with spheroidal aspect ratio)
try:
    import rockphypy
    from rockphypy import EM

    _ROCKPHY_AVAILABLE = True
except Exception:
    _ROCKPHY_AVAILABLE = False


@dataclass
class DEMSettings:
    """
    Settings for Differential Effective Medium (DEM) modeling of melt inclusions.

    Parameters
    ----------
    aspect_ratio : float
        Spheroidal inclusion aspect ratio α. Use:
          - α = 1.0 for spherical inclusions,
          - α < 1 for oblate (disk/film-like) spheroids typical of textural equilibrium,
          - α > 1 for prolate (tube-like) spheroids.
        Practical ranges:
          - α ≈ 0.10–0.15 are often used to emulate texturally equilibrated melt pockets
            controlled by dihedral angle (Takei, 2002). [4](https://agupubs.onlinelibrary.wiley.com/doi/epdf/10.1029/2001JB000522)
    enforce_phi_crit : bool
        If True, apply a soft clamp at the critical porosity (rigidity loss).
        This is a pragmatic safeguard; for a rigorous percolation-aware DEM,
        see modified DEM approaches (Mukerji et al., 1995). [5](https://www.osti.gov/biblio/183353)[6](https://earthref.org/ERR/15548/)
    phi_crit : float
        Critical porosity (volume fraction of inclusions) at which the aggregate
        is assumed to lose rigidity. Common values are ~0.3–0.4 in granular networks,
        though the exact value depends on microstructure and topology. [5](https://www.osti.gov/biblio/183353)

    Notes
    -----
    This settings holder allows you to switch between spherical and spheroidal
    DEM behavior by varying α, and optionally enforce a qualitative percolation cap.
    """

    aspect_ratio: float = 1.0
    enforce_phi_crit: bool = False
    phi_crit: float = 0.35


# Reasonable defaults for mantle/peridotite + basaltic melt
DEFAULTS = {
    "K_host_GPa": 125.0,  # peridotitic aggregate baseline (bulk modulus) [2](https://www.cambridge.org/core/books/rock-physics-handbook/A53F53ADFDD5D72EF01A9E4C6E9454A7)
    "G_host_GPa": 75.0,  # peridotitic aggregate baseline (shear modulus) [2](https://www.cambridge.org/core/books/rock-physics-handbook/A53F53ADFDD5D72EF01A9E4C6E9454A7)
    "rho_kg_m3": 3300.0,  # peridotitic aggregate density (upper mantle) [2](https://www.cambridge.org/core/books/rock-physics-handbook/A53F53ADFDD5D72EF01A9E4C6E9454A7)
    "K_melt_GPa": 15.0,  # basaltic melt compressibility regime [2](https://www.cambridge.org/core/books/rock-physics-handbook/A53F53ADFDD5D72EF01A9E4C6E9454A7)
    "G_melt_GPa": 0.0,  # fluid melt shear ~ 0; standard assumption in effective media [3](https://rockphypy.readthedocs.io/en/latest/getting_started/10_Differential_effective_medium_model.html)
    "alpha": 0.10,  # textural equilibrium (oblate spheroids) [4](https://agupubs.onlinelibrary.wiley.com/doi/epdf/10.1029/2001JB000522)
    "phi_crit": 0.35,  # optional soft clamp for rigidity loss (modified DEM literature) [5](https://www.osti.gov/biblio/183353)
}


class SeismicDEM:
    """
    Differential Effective Medium (DEM) solver for seismic velocities in partially molten rocks.

    Purpose
    -------
    Compute the effective bulk modulus (K_eff) and shear modulus (G_eff) of a
    two-phase composite (solid matrix + melt inclusions) as functions of melt fraction φ,
    inclusion shape (via aspect ratio α), and phase moduli (host and inclusion).
    Then convert K_eff, G_eff, and density ρ to Vp and Vs:
        Vp = sqrt( (K_eff + 4*G_eff/3) / ρ ),  Vs = sqrt( G_eff / ρ ).

    Background
    ----------
    DEM treats the composite by incrementally adding inclusions to a host,
    updating the effective moduli via coupled ODEs with strain concentration
    factors derived from Eshelby tensors. Berryman developed widely used
    effective medium formulations for elastic composites; modern treatments and
    tutorials (e.g., rockphypy) implement DEM with spheroidal aspect ratio α
    for versatile pore/melt geometries. [1](https://sepwww.stanford.edu/data/media/public/docs/sep138/jim1/paper.pdf)[3](https://rockphypy.readthedocs.io/en/latest/getting_started/10_Differential_effective_medium_model.html)

    Behavior
    --------
    - If `rockphypy` is installed and α ≠ 1, the class delegates to its
      `EM.Berryman_DEM` solver for spheroidal inclusions (preferred).
    - Otherwise, it uses an in-house spherical inclusion path (α = 1) with
      analytic strain concentration factors P and Q.

    Assumptions
    -----------
    - Long-wavelength limit (inclusions much smaller than seismic wavelength),
      dilute-to-moderate inclusion concentrations, and isotropic behavior unless
      an anisotropic crack model (e.g., Hudson) is adopted separately. [7](https://academic.oup.com/gji/article/64/1/133/635705)
    - Melt treated as a fluid: μ_inclusion ≈ 0. This is standard in effective media. [3](https://rockphypy.readthedocs.io/en/latest/getting_started/10_Differential_effective_medium_model.html)

    Parameters
    ----------
    settings : DEMSettings
        Control aspect ratio α and optional critical porosity clamp.

    # filename: src/seismic_dem.py  (add these defaults near the top)
    suggested_defaults = {
        "K_host_GPa": 125.0,   # peridotitic aggregate baseline  [1](https://www.cambridge.org/core/books/rock-physics-handbook/rock-physics-handbook/00B97486A56C2F4EBBC6322280FD71D4)
        "G_host_GPa": 75.0,    # peridotitic aggregate baseline  [1](https://www.cambridge.org/core/books/rock-physics-handbook/rock-physics-handbook/00B97486A56C2F4EBBC6322280FD71D4)
        "rho_kg_m3": 3300.0,   # peridotitic aggregate baseline
        "K_melt_GPa": 15.0,    # silicate melt compressibility   [2](https://www.cambridge.org/core/books/rock-physics-handbook/A53F53ADFDD5D72EF01A9E4C6E9454A7)
        "G_melt_GPa": 0.0,     # fluid melt shear ~ 0            [3](https://rockphypy.readthedocs.io/en/latest/getting_started/10_Differential_effective_medium_model.html)
        "alpha": 0.10,         # textural equilibrium, oblate    [4](https://agupubs.onlinelibrary.wiley.com/doi/epdf/10.1029/2001JB000522)
        "phi_crit": 0.35       # optional soft clamp             [5](https://www.osti.gov/biblio/183353)[6](https://earthref.org/ERR/15548/)
    }


    See also
    --------
    - Berryman, J.G.: Effective medium theory for elastic composites. [1](https://sepwww.stanford.edu/data/media/public/docs/sep138/jim1/paper.pdf)
    - Rock Physics Handbook: Effective media, bounds, and mixing laws. [2](https://www.cambridge.org/core/books/rock-physics-handbook/A53F53ADFDD5D72EF01A9E4C6E9454A7)
    - rockphypy documentation: Differential Effective Medium (DEM) examples. [3](https://rockphypy.readthedocs.io/en/latest/getting_started/10_Differential_effective_medium_model.html)
    """

    def __init__(self, settings: DEMSettings = DEMSettings()):
        self.settings = settings

    # ---------- Spherical (analytic) path ----------
    @staticmethod
    def _zeta_m(Km: float, Gm: float) -> float:
        """
        Compute ζ_m, the effective viscoelastic parameter used in spherical inclusion
        strain concentration for the deviatoric response.

        Definition
        ----------
        ζ_m = μ_m * (9*K_m + 8*μ_m) / (6*(K_m + 2*μ_m))

        Role
        ----
        ζ_m enters the deviatoric strain concentration factor Q for spherical inclusions,
        capturing the coupling of bulk and shear in the host’s response. This expression
        is standard in effective medium formulations and used in open tutorials and
        implementations (e.g., rockphypy’s DEM examples). [3](https://rockphypy.readthedocs.io/en/latest/getting_started/10_Differential_effective_medium_model.html)

        Parameters
        ----------
        Km : float
            Host bulk modulus in Pascals.
        Gm : float
            Host shear modulus in Pascals.

        Returns
        -------
        float
            ζ_m in Pascals.

        Notes
        -----
        Ensure units are consistent (Pascals) as seismic velocities scale with moduli/ρ.
        """
        return Gm * (9.0 * Km + 8.0 * Gm) / (6.0 * (Km + 2.0 * Gm))

    @staticmethod
    def _P_spherical(Km: float, Gm: float, Ki: float) -> float:
        """
        Volumetric strain concentration factor P for spherical fluid/solid inclusions.

        Definition
        ----------
        P = (K_m + 4*μ_m/3) / (K_i + 4*μ_m/3)

        Interpretation
        --------------
        P modulates how the inclusion’s bulk modulus K_i contrasts with the host’s
        combined volumetric stiffness (K_m + 4*μ_m/3), affecting dK_eff/dφ in DEM.
        This expression is from classical spherical inclusion theory in effective media
        and is used in DEM tutorials and code examples. [3](https://rockphypy.readthedocs.io/en/latest/getting_started/10_Differential_effective_medium_model.html)

        Parameters
        ----------
        Km : float
            Host bulk modulus in Pascals.
        Gm : float
            Host shear modulus in Pascals.
        Ki : float
            Inclusion bulk modulus in Pascals (e.g., silicate melt ~10–25 GPa). [2](https://www.cambridge.org/core/books/rock-physics-handbook/A53F53ADFDD5D72EF01A9E4C6E9454A7)

        Returns
        -------
        float
            Dimensionless P.

        Notes
        -----
        For fluid melt, μ_i ≈ 0, but K_i is finite; P reflects this finite compressibility.
        """
        return (Km + 4.0 * Gm / 3.0) / (Ki + 4.0 * Gm / 3.0)

    @staticmethod
    def _Q_spherical(Km: float, Gm: float, Gi: float) -> float:
        """
        Deviatoric strain concentration factor Q for spherical inclusions.

        Definition
        ----------
        Q = (μ_m + ζ_m) / (μ_i + ζ_m),
        where ζ_m = μ_m * (9*K_m + 8*μ_m) / (6*(K_m + 2*μ_m)).

        Interpretation
        --------------
        Q accounts for shear compliance contrast between inclusion and host. For a fluid
        inclusion (μ_i ≈ 0), Q > 1, indicating enhanced deviatoric strain in the host and
        strong reduction of G_eff as φ increases. This formula is standard in spherical
        inclusion treatments and is used in practical DEM examples (e.g., rockphypy). [3](https://rockphypy.readthedocs.io/en/latest/getting_started/10_Differential_effective_medium_model.html)

        Parameters
        ----------
        Km : float
            Host bulk modulus in Pascals.
        Gm : float
            Host shear modulus in Pascals.
        Gi : float
            Inclusion shear modulus in Pascals (≈ 0 for melt). [3](https://rockphypy.readthedocs.io/en/latest/getting_started/10_Differential_effective_medium_model.html)

        Returns
        -------
        float
            Dimensionless Q.
        """
        zeta = SeismicDEM._zeta_m(Km, Gm)
        return (Gm + zeta) / (Gi + zeta)

    def _dem_integrate_spherical(
        self,
        phi: float,
        K_host: float,
        G_host: float,
        K_incl: float,
        G_incl: float,
        n_steps: int = 400,
    ) -> float | float:
        """
        Integrate the DEM ODEs for spherical inclusions from φ=0 to target φ.

        Equations
        ---------
        (1 - y) dK_eff/dy = (K_i - K_eff) * P,
        (1 - y) dμ_eff/dy = (μ_i - μ_eff) * Q,
        with K_eff(0) = K_host, μ_eff(0) = G_host,
        and P, Q the spherical strain concentration factors (see `_P_spherical`, `_Q_spherical`). [3](https://rockphypy.readthedocs.io/en/latest/getting_started/10_Differential_effective_medium_model.html)

        Numerical method
        ----------------
        Forward Euler over y ∈ [0, φ] with `n_steps` increments. This is sufficient for
        interactive modeling and moderate φ; for high precision or stiff behavior, a
        higher-order ODE integrator can be substituted.

        Parameters
        ----------
        phi : float
            Melt fraction (0–1).
        K_host : float
            Host bulk modulus [Pa].
        G_host : float
            Host shear modulus [Pa].
        K_incl : float
            Inclusion bulk modulus [Pa].
        G_incl : float
            Inclusion shear modulus [Pa]; ~0 for a fluid melt. [3](https://rockphypy.readthedocs.io/en/latest/getting_started/10_Differential_effective_medium_model.html)
        n_steps : int
            Integration steps over y; default 400.

        Returns
        -------
        float | float
            K_eff [Pa], G_eff [Pa] at melt fraction φ.

        Notes
        -----
        - Units must be SI (Pascals) for consistent Vp/Vs conversion.
        - This path is **isotropic**; crack‑induced anisotropy requires Hudson models if needed. [7](https://academic.oup.com/gji/article/64/1/133/635705)
        """
        phi = float(np.clip(phi, 0.0, 0.999))
        Km, Gm = float(K_host), float(G_host)
        ys = np.linspace(0.0, phi, n_steps + 1)
        for j in range(n_steps):
            y = ys[j]
            P = self._P_spherical(Km, Gm, K_incl)
            Q = self._Q_spherical(Km, Gm, G_incl)
            dK_dy = (K_incl - Km) * P / (1.0 - y + 1e-12)
            dG_dy = (G_incl - Gm) * Q / (1.0 - y + 1e-12)
            Km += dK_dy * (phi / n_steps)
            Gm += dG_dy * (phi / n_steps)
            Km = max(Km, 1e-9)
            Gm = max(Gm, 1e-9)
        return Km, Gm

    def _dem_via_rockphypy(
        self, phi: float, K_host: float, G_host: float, K_incl: float, G_incl: float
    ) -> float | float:
        """
        Compute DEM effective moduli using `rockphypy.EM.Berryman_DEM` for spheroidal inclusions.

        Implementation
        --------------
        The `rockphypy` package implements Berryman’s DEM solver with spheroidal Eshelby
        concentration factors and exposes the inclusion aspect ratio α. We delegate to
        this solver when α ≠ 1.0 and the package is available. [3](https://rockphypy.readthedocs.io/en/latest/getting_started/10_Differential_effective_medium_model.html)

        Parameters
        ----------
        phi : float
            Melt fraction (0–1). Passed to `tStop` (porosity) in `rockphypy`.
        K_host : float
            Host bulk modulus [Pa]. Converted to GPa for the solver.
        G_host : float
            Host shear modulus [Pa]. Converted to GPa for the solver.
        K_incl : float
            Inclusion bulk modulus [Pa]. Converted to GPa for the solver.
        G_incl : float
            Inclusion shear modulus [Pa]. Converted to GPa for the solver.

        Returns
        -------
        float | float
            K_eff [Pa], G_eff [Pa] at melt fraction φ.

        Notes
        -----
        - If the `rockphypy` call fails for any reason, the code falls back to the spherical path.
        - This path remains **isotropic**; anisotropy from aligned cracks would require Hudson. [7](https://academic.oup.com/gji/article/64/1/133/635705)
        """
        K0_GPa, G0_GPa = K_host / 1e9, G_host / 1e9
        Ki_GPa, Gi_GPa = K_incl / 1e9, G_incl / 1e9

        alpha = float(self.settings.aspect_ratio)
        tStop = float(phi)  # porosity fraction

        K_arr, G_arr, y_arr = EM.Berryman_DEM(
            K0_GPa, G0_GPa, Ki_GPa, Gi_GPa, alpha, tStop
        )  # [3](https://rockphypy.readthedocs.io/en/latest/getting_started/10_Differential_effective_medium_model.html)
        K_eff_GPa = float(K_arr[-1])
        G_eff_GPa = float(G_arr[-1])
        return K_eff_GPa * 1e9, G_eff_GPa * 1e9

    # ---------- Public API ----------
    def effective_moduli(
        self,
        phi: float,
        K_host: float,
        G_host: float,
        K_incl: float,
        G_incl: float = 0.0,
        n_steps: int = 400,
    ) -> float | float:
        """
        Compute effective moduli (K_eff, G_eff) at melt fraction φ with spheroidal support.

        Behavior
        --------
        - If `rockphypy` is present and `aspect_ratio != 1.0`, use the spheroidal DEM path
          (preferred for α ≠ 1.0).
        - Otherwise use the analytic spherical DEM path with explicit P and Q.

        Parameters
        ----------
        phi : float
            Melt fraction (0–1).
        K_host : float
            Host bulk modulus [Pa].
        G_host : float
            Host shear modulus [Pa].
        K_incl : float
            Inclusion bulk modulus [Pa].
        G_incl : float, default=0.0
            Inclusion shear modulus [Pa]. For melt, set to ~0. [3](https://rockphypy.readthedocs.io/en/latest/getting_started/10_Differential_effective_medium_model.html)
        n_steps : int, default=400
            Integration steps for the spherical path.

        Returns
        -------
        float | float
            K_eff [Pa], G_eff [Pa] at φ.

        Percolation
        -----------
        If `enforce_phi_crit` is True and φ ≥ `phi_crit`, this method returns small
        moduli (soft clamp). For rigorous critical-porosity constraints, consider
        modified DEM formulations (Mukerji et al., 1995). [5](https://www.osti.gov/biblio/183353)[6](https://earthref.org/ERR/15548/)

        References
        ----------
        - Berryman effective medium theory (elastic composites). [1](https://sepwww.stanford.edu/data/media/public/docs/sep138/jim1/paper.pdf)
        - Rock Physics Handbook (effective media and bounds). [2](https://www.cambridge.org/core/books/rock-physics-handbook/A53F53ADFDD5D72EF01A9E4C6E9454A7)
        - rockphypy DEM spheroidal implementation (aspect ratio α). [3](https://rockphypy.readthedocs.io/en/latest/getting_started/10_Differential_effective_medium_model.html)
        """
        phi = float(np.clip(phi, 0.0, 0.999))

        if self.settings.enforce_phi_crit and phi >= self.settings.phi_crit:
            eps = 1e-6
            return eps, eps

        if _ROCKPHY_AVAILABLE and (abs(self.settings.aspect_ratio - 1.0) > 1e-6):
            try:
                return self._dem_via_rockphypy(phi, K_host, G_host, K_incl, G_incl)
            except Exception:
                # Fallback if external solver fails
                pass

        return self._dem_integrate_spherical(
            phi, K_host, G_host, K_incl, G_incl, n_steps=n_steps
        )

    def compute(
        self,
        rho: float,
        phi: float,
        K_host: float,
        G_host: float,
        K_incl: float,
        G_incl: float = 0.0,
    ) -> float | float:
        """
        Compute seismic velocities (Vp, Vs) from DEM-updated moduli at melt fraction φ.

        Pipeline
        --------
        1) Compute (K_eff, G_eff) via `effective_moduli()` with spherical or spheroidal DEM.
        2) Convert to velocities using:
           Vp = sqrt( (K_eff + 4*G_eff/3) / ρ ),  Vs = sqrt( G_eff / ρ ).

        Parameters
        ----------
        rho : float
            Density [kg/m^3] of the aggregate (assumed unchanged by small φ).
        phi : float
            Melt fraction (0–1).
        K_host : float
            Host bulk modulus [Pa].
        G_host : float
            Host shear modulus [Pa].
        K_incl : float
            Inclusion bulk modulus [Pa].
        G_incl : float, default=0.0
            Inclusion shear modulus [Pa] (≈ 0 for melt). [3](https://rockphypy.readthedocs.io/en/latest/getting_started/10_Differential_effective_medium_model.html)

        Returns
        -------
        float | float
            Vp [m/s], Vs [m/s] at φ.

        Notes
        -----
        - This path is isotropic; aligned cracks need anisotropic models (Hudson). [7](https://academic.oup.com/gji/article/64/1/133/635705)
        - For textural equilibrium melt pockets, set α ≈ 0.10–0.15 in settings. [4](https://agupubs.onlinelibrary.wiley.com/doi/epdf/10.1029/2001JB000522)
        """
        K_eff, G_eff = self.effective_moduli(phi, K_host, G_host, K_incl, G_incl)
        vp = np.sqrt((K_eff + 4.0 * G_eff / 3.0) / rho)
        vs = np.sqrt(G_eff / rho)
        return float(vp), float(vs)

    # Convenience wrapper with defaults
    def vp_vs_defaults(
        self,
        phi: float,
        K_host_GPa: float = DEFAULTS["K_host_GPa"],
        G_host_GPa: float = DEFAULTS["G_host_GPa"],
        rho_kg_m3: float = DEFAULTS["rho_kg_m3"],
        K_melt_GPa: float = DEFAULTS["K_melt_GPa"],
        G_melt_GPa: float = DEFAULTS["G_melt_GPa"],
    ) -> float | float:
        """
        Convenience method: DEM velocities with sensible defaults for mantle/peridotite + basaltic melt.

        Defaults (rationale)
        --------------------
        - Host moduli: K_host ≈ 125 GPa, G_host ≈ 75 GPa, ρ ≈ 3300 kg/m^3
          Representative of peridotitic aggregates at upper-mantle conditions. [2](https://www.cambridge.org/core/books/rock-physics-handbook/A53F53ADFDD5D72EF01A9E4C6E9454A7)
        - Melt moduli: K_melt ≈ 15 GPa, G_melt ≈ 0 GPa (fluid)
          Silicate melt compressibility ~10–25 GPa; shear ≈ 0 for fluids. [2](https://www.cambridge.org/core/books/rock-physics-handbook/A53F53ADFDD5D72EF01A9E4C6E9454A7)[3](https://rockphypy.readthedocs.io/en/latest/getting_started/10_Differential_effective_medium_model.html)
        - Aspect ratio α (in `self.settings`): default 0.10 for oblate spheroids, consistent
          with textural equilibrium melt pocket geometry (dihedral-angle control). [4](https://agupubs.onlinelibrary.wiley.com/doi/epdf/10.1029/2001JB000522)

        Parameters
        ----------
        phi : float
            Melt fraction (0–1).
        K_host_GPa : float, default=125.0
            Host bulk modulus [GPa].
        G_host_GPa : float, default=75.0
            Host shear modulus [GPa].
        rho_kg_m3 : float, default=3300.0
            Aggregate density [kg/m^3].
        K_melt_GPa : float, default=15.0
            Melt bulk modulus [GPa].
        G_melt_GPa : float, default=0.0
            Melt shear modulus [GPa].

        Returns
        -------
        float | float
            Vp [m/s], Vs [m/s] at φ using defaults and current `settings.aspect_ratio`.

        Notes
        -----
        To emulate different regimes:
        - Gabbroic lower crust: K_host≈90 GPa, G_host≈35 GPa, ρ≈3000 kg/m^3 (update arguments).
        - Spherical comparison: set `settings.aspect_ratio=1.0`.
        - Crack-like (very thin): set α≪0.1; for anisotropy, consider Hudson models. [7](https://academic.oup.com/gji/article/64/1/133/635705)
        """
        if self.settings.aspect_ratio is None:
            self.settings.aspect_ratio = DEFAULTS["alpha"]

        if self.settings.enforce_phi_crit and phi >= (
            self.settings.phi_crit or DEFAULTS["phi_crit"]
        ):
            epsK = epsG = 1e-6
            vp = np.sqrt((epsK + 4.0 * epsG / 3.0) / rho_kg_m3)
            vs = np.sqrt(epsG / rho_kg_m3)
            return float(vp), float(vs)

        K_host, G_host = K_host_GPa * 1e9, G_host_GPa * 1e9
        K_melt, G_melt = K_melt_GPa * 1e9, G_melt_GPa * 1e9
        return self.vp_vs(rho_kg_m3, phi, K_host, G_host, K_melt, G_melt)


# ----------------------------------------
# 5) Joint forward model & simple inversion
# ----------------------------------------


class JointMeltEstimator:
    """
    Combines electrical and seismic predictions; grid-search inversion for φ.
    """

    def __init__(
        self,
        melt_cond_model: MeltConductivityModel,
        archie_model: ModifiedArchieModel,
        elastic_agg: ElasticAggregate,
        seismic_reduction: SeismicMeltReduction,
    ):
        self.melt_cond_model = melt_cond_model
        self.archie = archie_model
        self.elastic_agg = elastic_agg
        self.seis = seismic_reduction

    def forward(
        self, phi: float, T_K: float, comp: Dict[str, float]
    ) -> Dict[str, float]:
        sigma_melt = self.melt_cond_model.compute(T_K, comp)
        sigma_bulk = self.archie.conductivity(phi, sigma_melt)
        vp = self.seis.vp(self.elastic_agg.vp_ms, phi)
        vs = self.seis.vs(self.elastic_agg.vs_ms, phi)
        return {
            "phi": phi,
            "sigma_melt": sigma_melt,
            "sigma_bulk": sigma_bulk,
            "rho_bulk_Ohm_m": 1.0 / sigma_bulk,
            "vp_ms": vp,
            "vs_ms": vs,
        }

    def invert_phi(
        self,
        target_sigma_bulk_S: Optional[float] = None,
        target_rho_bulk_Ohm_m: Optional[float] = None,
        target_vp_ms: Optional[float] = None,
        T_K: float = 1473.0,
        comp: Dict[str, float] = None,
        phi_bounds: Tuple[float, float] = (0.0, 0.4),
        n_grid: int = 401,
    ) -> Dict[str, float]:
        comp = comp or {}
        phis = np.linspace(phi_bounds[0], phi_bounds[1], n_grid)
        sigma_melt = self.melt_cond_model.compute(T_K, comp)
        vp0 = self.elastic_agg.vp_ms

        misfits = []
        for phi in phis:
            sigma_bulk = self.archie.conductivity(phi, sigma_melt)
            rho_bulk = 1.0 / sigma_bulk
            vp = self.seis.vp(vp0, phi)

            m = 0.0
            if target_sigma_bulk_S is not None:
                m += (sigma_bulk - target_sigma_bulk_S) ** 2
            if target_rho_bulk_Ohm_m is not None:
                m += (rho_bulk - target_rho_bulk_Ohm_m) ** 2
            if target_vp_ms is not None:
                m += (vp - target_vp_ms) ** 2
            misfits.append(m)

        idx = int(np.argmin(misfits))
        best_phi = float(phis[idx])
        result = self.forward(best_phi, T_K, comp)
        result["misfit"] = float(misfits[idx])
        return result


# ----------------------------------
# 6) Convenience: default models & alphaMELTS glue
# ----------------------------------


def build_default_models():
    melt_cond = MeltConductivityModel(
        sigma0_S=400.0,  # S/m
        Ea_J=1.7e5,  # J/mol
        kH_J=3.0e4,  # H2O raises conductivity
        kC_J=-1.0e4,  # CO2 often reduces it (net effect depends on system)
        kR_J=0.0,
    )
    archie = ModifiedArchieModel(C=0.75, n=1.1, phi_c=0.01, sigma_solid_S=0.01)
    elastic = ElasticAggregate(K_GPa=125.0, G_GPa=75.0, rho_kg_m3=3300.0)
    seismic = SeismicMeltReduction(a_vp=1.2, a_vs=2.0)
    return melt_cond, archie, elastic, seismic


# alphaMELTS integration
def build_models_from_alphamelts(
    run_dir: str,
    step_index: Optional[int] = None,
    T_target_C: Optional[float] = None,
    P_target_kbar: Optional[float] = None,
):
    from .alphamelts_io import AlphaMELTSLoader

    loader = AlphaMELTSLoader(run_dir)
    steps = loader.load()
    if not steps:
        raise FileNotFoundError(
            "No alphaMELTS steps parsed. Check melts-liquid.tbl / melts.out in the run directory."
        )
    if step_index is None:
        idx = loader.nearest_step(T_target_C=T_target_C, P_target_kbar=P_target_kbar)
    else:
        idx = int(np.clip(step_index, 0, len(steps) - 1))
    melts_state = loader.to_melts_state(idx)

    models = build_default_models()
    return melts_state, models
