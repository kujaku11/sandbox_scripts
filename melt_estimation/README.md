# Melt Fraction Petrophysics (alphaMELTS → Archie + Seismic)

This repository provides a class‑based Python workflow to estimate melt fraction by jointly modeling **electrical resistivity** (modified Archie's law) and **seismic P-wave velocity** (first‑order melt sensitivity), using **alphaMELTS** / **MELTS** outputs for composition and phase proportions. It includes a **Panel + Bokeh** application to explore parameter space interactively.

## Why this approach?

- **alphaMELTS/MELTS** yields the **thermodynamic state**: melt composition, temperature, pressure, and phase proportions per equilibrium step, with tabular outputs (`melts-liquid.tbl`) and comprehensive logs (`melts.out`). We read these to set petrophysical parameters and compute melt fraction \(\phi\) by mass. [1](https://academic.oup.com/nsr/article/8/11/nwab064/6223473)  
- **Modified Archie’s law** captures the strong conductivity increase once melt **percolates**, using a connectivity factor \(C\), exponent \(n\), and percolation threshold \(\phi_c\); its behavior in partial melts and composition dependence are well documented in lab/field studies. [3](https://petthermotools.readthedocs.io/en/latest/Installation/InstallationScript.html),[4](https://magmasource.caltech.edu/alphamelts/)  
- **Seismic reduction** uses a first‑order linear sensitivity for \(V_p(\phi)\) and \(V_s(\phi)\), consistent with effective‑medium expectations for texturally equilibrated melt pockets; pore shape effects (aspect ratio) can be incorporated later via DEM/Hudson style models. [5](https://magmasource.caltech.edu/alphamelts/1/alphamelts_manual.pdf),[6](https://thermoengine.readthedocs.io/en/latest/MELTS-v1.1.0-equilibrium.html)

> Optional future integration: **USGS MinVel** to compute zero‑porosity aggregate \(K,G,\rho\) from mineral modes at the MELTS step T,P (Python + NetCDF DB available). [7](https://www.cambridge.org/core/books/rock-physics-handbook/rock-physics-handbook/00B97486A56C2F4EBBC6322280FD71D4),[8](https://books.google.com/books/about/The_Rock_Physics_Handbook.html?id=FMS-DwAAQBAJ)

---

## Quick start

### 1) Create environment

```bash
conda env create -f env/environment.yml
conda activate mf-petro

# Example alphaMELTS Run Integration

1. Place your alphaMELTS outputs (`melts.out`, `melts-liquid.tbl`) in a folder.
2. Start the Panel app:

```bash
panel serve src/app_melt_panel.py --show