# MELTS_MT Python Workflow

This tutorial walks through three stages using the `melts_mt.py` module built earlier in this conversation:

1. **Estimate melt properties** — either from a real alphaMELTS run (`AlphaMeltsRun`) or from the empirical `volfrac()` emulator used in Cordell et al. (2022)
2. **Estimate bulk electrical resistivity** from those melt properties
3. **Plot the results**, adapted from `MELTS_Resistivity_Figs.m`

## Important distinction before you start

`MELTS_Resistivity_Figs.m` (the script you just shared) does **not** read a single alphaMELTS output file. Its "MELTS coupling" section sweeps the `volfrac()` emulator over a dense grid of `(H2O_sys, T)` pairs at fixed `P` — effectively querying thousands of "virtual" MELTS outcomes from a pre-fitted curve, to build a 2D parameter-space map (melt fraction vs. water vs. temperature).

A real alphaMELTS run instead gives you **one path** through that same space — e.g., a single crystallization sequence at decreasing T, with melt fraction, composition, and dissolved water evolving step by step.

These aren't competing approaches — they answer different questions:

| | Emulator grid (`volfrac()`) | Real alphaMELTS run (`AlphaMeltsRun`) |
|---|---|---|
| What you get | A full 2D map: "for *any* T and H2O_sys, what's the resistivity?" | One line: "for *this specific* bulk composition and cooling path, how does resistivity evolve?" |
| Composition | Fixed (baked into the `volfrac()` fit) | Whatever your actual alphaMELTS run used |
| Use case | Interpreting an MT resistivity anomaly broadly, without committing to one petrologic path | Testing a specific hypothesis about a specific magma body's crystallization history |

**Part A** below covers the real-alphaMELTS-run pathway. **Part B** reproduces the paper's own grid-based figures. **Part C** shows combining them.

All code assumes `melts_mt.py` (with `AlphaMeltsRun`, `volfrac`, `melt_rho`, `Keppler`, `MAL3`, `MAL`, `MAL_solve_phi`, `hashim_crystal_resistivity`, etc.) is importable in the same directory.

---

## Part A — Melt properties and resistivity from a real alphaMELTS run

### A.1 — Inspect your output file first

Before writing a `column_map`, look at what you actually have:

```python
import pandas as pd

# Just peek at the raw file -- don't assume structure yet
with open("Phase_main_tbl.txt") as f:
    for i, line in enumerate(f):
        print(repr(line))
        if i > 5:
            break
```

alphaMELTS 1.x phase tables typically have a few header/metadata lines before the real column-header row, and use whitespace-delimited columns. Adjust `skiprows` / `comment` accordingly once you see the real structure. **I can't predict your exact file layout without seeing it** — if parsing fails, paste the first several lines and I'll fix the mapping.

### A.2 — Load the run and map columns

```python
from melts_mt import AlphaMeltsRun

# EXAMPLE column_map -- replace the right-hand side strings with YOUR
# file's actual header names once you've inspected it (step A.1)
column_map = {
    "T": "Temperature",          # degrees C (or K -- set temperature_units below)
    "P": "Pressure",             # bars (or MPa/GPa -- set pressure_units below)
    "melt_mass_frac": "liquid_0", # mass or mass fraction of the liquid phase
    "solid_mass_frac": "solid_mass_sum",  # mass or mass fraction of all solids
    "fluid_mass_frac": "fluid_0", # mass or mass fraction of exsolved fluid (if present)
    "H2O_melt": "H2O",           # wt% dissolved H2O in the liquid
    # Optional: include if you want melt oxide composition carried through
    # for later use (e.g. a custom composition-aware conductivity law)
    "SiO2": "SiO2", "MgO": "MgO", "FeO": "FeO", "CaO": "CaO",
    "Na2O": "Na2O", "K2O": "K2O", "Al2O3": "Al2O3",
}

run = AlphaMeltsRun.from_file(
    "Phase_main_tbl.txt",
    column_map=column_map,
    temperature_units="C",     # or "K"
    pressure_units="bar",      # or "MPa" / "GPa"
    mass_basis="mass",         # "mass" if columns are absolute masses needing
                                # normalization; "fraction" if already 0-1
    skiprows=3,                # adjust based on A.1 inspection
)

print(f"Loaded {len(run.steps)} steps")
print(f"First step: T={run.steps[0].T_C:.1f} C, "
      f"melt fraction={run.steps[0].eps_m:.3f}, "
      f"dissolved H2O={run.steps[0].H2O_melt:.2f} wt%")
```

### A.3 — Compute resistivity along the real trajectory

```python
results = run.compute_resistivity_profile(
    c=1.15,          # melt connectivity exponent (paper uses 1.0-1.5 typically)
    rhoh=None,        # None -> use Hashim et al. (2013) T-dependent default
    volflag=True,     # True: handle any exsolved-fluid steps properly rather
                       # than NaN-ing them out (see note in AlphaMeltsRun docstring)
    concentration=1.0, # NaCl-equivalent wt% for any exsolved fluid
    cf=3.0,            # volatile connectivity exponent
    melt_flag=1,       # 1 = rhyolite, Guo et al. (2016) -- change if your
                       # run is basaltic/andesitic/dacitic (see melt_rho docstring)
)

df = run.to_dataframe(c=1.15, volflag=True, concentration=1.0, cf=3.0, melt_flag=1)
print(df.head())
```

`df` now has one row per step with columns: `T_C`, `P_MPa`, `eps_h`, `eps_m`, `eps_g`, `H2O_melt`, `rhoh`, `rhom`, `rhof`, `rhob`, plus any oxide columns you included in `column_map`.

### A.4 — Quick diagnostic plots

```python
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 3, figsize=(15, 4))

axes[0].plot(df["T_C"], df["eps_m"], '-o', ms=3)
axes[0].set_xlabel("Temperature (°C)")
axes[0].set_ylabel("Melt fraction")
axes[0].set_title("Crystallization path")

axes[1].semilogy(df["T_C"], df["rhob"], '-o', ms=3, color='k')
axes[1].set_xlabel("Temperature (°C)")
axes[1].set_ylabel("Bulk resistivity (Ω·m)")
axes[1].set_title("Resistivity evolution")

axes[2].plot(df["T_C"], df["H2O_melt"], '-o', ms=3, color='tab:blue')
axes[2].set_xlabel("Temperature (°C)")
axes[2].set_ylabel("Dissolved melt H2O (wt%)")
axes[2].set_title("Melt water content")

plt.tight_layout()
plt.show()
```

---

## Part B — Reproducing the paper's parameter-space figures (grid emulator)

This directly mirrors `MELTS_Resistivity_Figs.m`, using the same `volfrac()`/`melt_rho()`/`Keppler()`/`MAL3()` emulator approach rather than a real alphaMELTS run — because this is genuinely what that script does.

### B.1 — Case study configuration

Transcribed directly from the MATLAB `case_study` switch block:

```python
import numpy as np

CASE_STUDIES = {
    0: dict(  # Synthetic
        name="Synthetic",
        w=np.arange(0.25, 6.0001, 0.01),
        H2O_sys=np.arange(0.25, 6.0001, 0.01),
        T=np.arange(700, 1000.001, 1),
        P=150, rhoh_fixed=1000, c=1.5, labflag=1,
        T1=np.nan, T2=np.nan, w1=np.nan, w2=np.nan,
        rhob_fixed=[1], concentration=0, mf=10,
    ),
    1: dict(  # Mono Basin
        name="Mono Basin",
        w=np.arange(0.25, 7.0001, 0.01),
        H2O_sys=np.arange(0.25, 3.0001, 0.01),
        T=np.arange(700, 950.001, 1),
        P=250, rhoh_fixed=1000, c=1.05, labflag=1,
        T1=750, T2=850, w1=4, w2=5,
        rhob_fixed=[6.5, 3, 10], concentration=0, mf=10,
    ),
    2: dict(  # Newberry
        name="Newberry",
        w=np.arange(0.25, 4.5001, 0.01),
        H2O_sys=np.arange(0.25, 4.5001, 0.01),
        T=np.arange(725, 950.001, 1),
        P=100, rhoh_fixed=1000, c=1.5, labflag=1,
        T1=850, T2=850, w1=1.5, w2=1.5,
        rhob_fixed=[25], concentration=1, mf=2,
    ),
    3: dict(  # LdMVF (Laguna del Maule)
        name="LdMVF",
        w=np.arange(0.25, 5.5001, 0.01),
        H2O_sys=np.arange(0.25, 5.5001, 0.01),
        T=np.arange(725, 1100.001, 1),
        P=100, rhoh_fixed=1000, c=1.5, labflag=1,
        T1=760, T2=850, w1=4, w2=5,
        rhob_fixed=[0.3], concentration=16, mf=1,
    ),
}

case_study = 3
cfg = CASE_STUDIES[case_study]
print(f"Running case study: {cfg['name']}")
```

**Note on `mf` (volatile connectivity):** the MATLAB script sets this per case study based on an assumed volatile-phase topology (10 = effectively disconnected/ignored, 2 = poorly-connected bubbles, 1 = well-connected brine lens). This is a modeling *assumption*, not something derived from data — worth treating as a sensitivity parameter in your own work rather than taking the paper's specific values as universal.

### B.2 — Melt resistivity map (w–T space) — reproduces Figure 1a

```python
from melts_mt import melt_rho, MAL, MAL_solve_phi, Keppler, volfrac, MAL3, hashim_crystal_resistivity

w, T, P, labflag = cfg["w"], cfg["T"], cfg["P"], cfg["labflag"]

sigm = np.full((len(w), len(T)), np.nan)
for i, w_i in enumerate(w):
    for j, T_j in enumerate(T):
        sigm[i, j] = melt_rho(P, T_j, w_i, labflag)

rhom_grid = 1.0 / sigm  # ohm-m, shape (len(w), len(T))
```

### B.3 — Bulk resistivity vs. melt resistivity & melt fraction — reproduces Figure 1b

```python
sigm_fixed = 1.0 / np.logspace(-1, 1, 200)  # a sweep of melt resistivities
chi = np.arange(0, 1.0001, 0.005)           # melt fraction sweep
c = cfg["c"]

sigb = np.full((len(chi), len(sigm_fixed)), np.nan)
for i, sm in enumerate(sigm_fixed):
    for j, ch in enumerate(chi):
        sigb[j, i] = MAL(0.001, sm, c, ch)  # 0.001 S/m ~ resistive host/crystal matrix

rhob_grid_b = 1.0 / sigb
```

### B.4 — Melt fraction as a function of (w, T) at fixed bulk resistivity — reproduces Figure 1c

```python
rhob_fixed = cfg["rhob_fixed"]
rhoh_fixed = cfg["rhoh_fixed"]

phi = np.full((len(w), len(T)), np.nan)
for i, w_i in enumerate(w):
    for j, T_j in enumerate(T):
        sigm_mid = melt_rho(P, T_j, w_i, labflag)
        phi[i, j] = MAL_solve_phi(rhob_fixed[0], rhoh_fixed, 1.0 / sigm_mid, c)

phi_plot = phi.copy()
phi_plot[phi_plot == 1] = 1.1  # match MATLAB's trick to visually distinguish 100% melt
```

### B.5 — Plot the 3-panel figure (reproduces MATLAB `figure(1)`)

```python
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# Panel (a): melt resistivity contours
ax = axes[0]
levels_major = 10.0 ** np.arange(-4, 5)
cs = ax.contour(w, T, rhom_grid.T, levels=levels_major, colors='k', linewidths=2)
ax.clabel(cs, inline=True, fontsize=8)
levels_minor = np.outer(np.arange(2, 10), 10.0 ** np.arange(-4, 5)).ravel()
ax.contour(w, T, rhom_grid.T, levels=sorted(levels_minor), colors='k',
           linewidths=0.5, linestyles='dashed')
ax.set_xlabel("Dissolved Water Content (wt%)")
ax.set_ylabel("Temperature (°C)")
ax.set_title("(a) Melt Resistivity (Ω·m)")

if not np.isnan(cfg["w1"]):
    w1, w2, T1, T2 = cfg["w1"], cfg["w2"], cfg["T1"], cfg["T2"]
    ax.add_patch(plt.Polygon([[w1, T1], [w2, T1], [w2, T2], [w1, T2]],
                               closed=True, facecolor='0.5', alpha=0.2))
    ax.plot(w1, T1, 'ok', mfc='b', ms=10)
    ax.plot(w2, T2, 'ok', mfc='r', ms=10)

# Panel (b): bulk resistivity in melt-resistivity/melt-fraction space
ax = axes[1]
rhom_fixed_vals = 1.0 / sigm_fixed
cs = ax.contour(rhom_fixed_vals, chi, rhob_grid_b, levels=levels_major,
                 colors='k', linewidths=2)
ax.clabel(cs, inline=True, fontsize=8)
ax.set_xscale("log")
ax.set_xlabel("Melt Resistivity (Ω·m)")
ax.set_ylabel("Melt Fraction")
ax.set_title("(b) Bulk Resistivity (Ω·m)")

if not np.isnan(cfg["T1"]):
    q1 = 1.0 / melt_rho(P, cfg["T1"], cfg["w1"], labflag)
    q2 = 1.0 / melt_rho(P, cfg["T2"], cfg["w2"], labflag)
    ax.axvline(q1, color='b', lw=2)
    ax.axvline(q2, color='r', lw=2)
    for rb in rhob_fixed:
        ax.contour(rhom_fixed_vals, chi, rhob_grid_b, levels=[rb],
                    colors='m', linewidths=2)

# Panel (c): melt fraction in (w, T) space at fixed bulk resistivity
ax = axes[2]
cmap = plt.get_cmap('viridis', 11)
pcm = ax.pcolormesh(w, T, phi_plot.T, cmap=cmap, vmin=0, vmax=1.1, shading='auto')
cb = fig.colorbar(pcm, ax=ax, ticks=np.arange(0, 1.1, 0.1))
cb.set_label("Melt Fraction")
cs = ax.contour(w, T, phi.T, levels=np.arange(0, 1.0001, 0.1), colors='k',
                 linewidths=1, linestyles='dotted')
ax.clabel(cs, inline=True, fontsize=7)
ax.set_xlabel("Dissolved H2O wt%")
ax.set_ylabel("Temperature (°C)")
ax.set_title(f"Fixed ρ_b = {rhob_fixed[0]} Ω·m")

if not np.isnan(cfg["w1"]):
    ax.add_patch(plt.Polygon([[w1, T1], [w2, T1], [w2, T2], [w1, T2]],
                               closed=True, facecolor='0.5', alpha=0.1))
    ax.plot(w1, T1, 'ok', mfc='b', ms=10)
    ax.plot(w2, T2, 'ok', mfc='r', ms=10)

plt.tight_layout()
plt.show()
```

### B.6 — Volatile resistivity vs. temperature — reproduces `figure(3)`

```python
T_arr = cfg["T"]
concentration1, concentration2 = 1, 16

rhof1 = np.array([1.0 / Keppler(P, Ti, concentration1, 1) for Ti in T_arr])
rhof2 = np.array([1.0 / Keppler(P, Ti, concentration2, 1) for Ti in T_arr])

fig, ax = plt.subplots(figsize=(8, 6))
ax.plot(T_arr, rhof1, '-k', lw=3, label='1 wt% NaCl Equivalent')
ax.plot(T_arr, rhof2, '--k', lw=3, label='16 wt% NaCl Equivalent')
ax.set_xlabel("Temperature (°C)")
ax.set_ylabel("Resistivity of Volatile Phase (Ω·m)")
ax.set_ylim(0, 10)
ax.legend()
ax.grid(True)
plt.show()
```

### B.7 — The full MELTS-coupled parameter space map — reproduces `figure(2)`

This is the core "MELTS coupling" section of the MATLAB script.

```python
H2O_sys = cfg["H2O_sys"]
mm = c
mf = cfg["mf"]
concentration = cfg["concentration"]

eps_h = np.full((len(T), len(H2O_sys)), np.nan)
eps_m = np.full_like(eps_h, np.nan)
eps_f = np.full_like(eps_h, np.nan)
H2O_m = np.full_like(eps_h, np.nan)
rhom = np.full_like(eps_h, np.nan)
rhob = np.full_like(eps_h, np.nan)
rhof = np.full(len(T), np.nan)

for i, T_i in enumerate(T):
    rhof[i] = 1.0 / Keppler(P, T_i, concentration, 1)
    for j, H2O_j in enumerate(H2O_sys):
        eh, em, ef, h2om = volfrac(P, T_i, H2O_j)
        eps_h[i, j], eps_m[i, j], eps_f[i, j], H2O_m[i, j] = eh, em, ef, h2om

        rhom[i, j] = 1.0 / melt_rho(P, T_i, h2om, labflag)
        rhob[i, j] = 1.0 / MAL3(1 / rhoh_fixed, 1 / rhom[i, j], 1 / rhof[i],
                                  eh, em, ef, mm, mf)
    if i % 50 == 0:
        print(f"T = {T_i} C done")

# --- post-processing, matching the MATLAB script's masking logic ---
cutoff = 0
mask_low_melt = eps_m <= cutoff
rhob[mask_low_melt] = np.nan
eps_f[mask_low_melt] = np.nan
eps_m[mask_low_melt] = np.nan

# NOTE: the MATLAB condition here was `if case_study <= 3`, which is true
# for EVERY defined case study (0-3) -- so in practice this masking is
# always applied, despite the comment suggesting it's only for the
# synthetic/Mono Basin cases. Preserved verbatim; flagging the
# comment/logic mismatch in case it wasn't intentional in the original.
rhob[eps_f > 0] = np.nan

H2O_m[eps_f > 0] = np.nan  # ignore dissolved melt H2O once saturated

# "liquidus" cutoff: treat eps_h <= 0.01 as fully molten
near_liquidus = eps_h <= 0.01
eps_h[near_liquidus] = 0
eps_m[near_liquidus] = 1 - eps_f[near_liquidus]

eps_m_plot = eps_m.copy()
eps_m_plot[eps_m_plot == 1] = 1.1
```

```python
fig, ax = plt.subplots(figsize=(9, 7))
cmap = plt.get_cmap('viridis', 11)
pcm = ax.pcolormesh(H2O_sys, T, eps_m_plot, cmap=cmap, vmin=0, vmax=1.1, shading='auto')
cb = fig.colorbar(pcm, ax=ax, ticks=np.arange(0, 1.1, 0.1))
cb.set_label("Melt Fraction")

# Saturation curve (eps_f transitions from 0 to >0)
ax.contour(H2O_sys, T, eps_f, levels=[1e-4], colors='k', linewidths=2)

# Liquidus curve (eps_h transitions across 0.01)
ax.contour(H2O_sys, T, eps_h, levels=[1e-2], colors='k', linewidths=2, linestyles='dashed')

# Bulk resistivity contours
levels = np.outer(10.0 ** np.arange(-2, 3), np.arange(1, 10)).ravel()
levels = np.sort(levels)
cs = ax.contour(H2O_sys, T, rhob, levels=levels, colors='k')
ax.clabel(cs, inline=True, fontsize=7)

ax.set_xlabel("Total System H2O wt%")
ax.set_ylabel("Temperature (°C)")
ax.set_xlim(H2O_sys.min(), H2O_sys.max())
ax.set_ylim(T.min(), T.max())
ax.set_title(f"{cfg['name']}: MELTS-coupled resistivity parameter space")

plt.tight_layout()
plt.show()
```

**Not yet ported:** the MATLAB script's final section — extracting the min/max melt fraction, temperature, and water content *along* a fixed bulk-resistivity contour — relies on `InterX.m` (generic curve intersection), which wasn't translated earlier since it wasn't on the main computation path. If you want that specific analysis (useful for quoting a "most likely melt fraction range" from an MT-derived resistivity value), `scipy`'s `shapely` library or `matplotlib`'s contour vertex extraction (similar to what was used in `melts_mt_magma_res()` earlier) can substitute — let me know if you want this built out.

---

## Part C — Overlaying a real alphaMELTS trajectory on the parameter-space map

This is likely the most useful combination: Part B gives you the resistivity landscape; Part A gives you where a real petrologic path sits within it.

```python
fig, ax = plt.subplots(figsize=(9, 7))
pcm = ax.pcolormesh(H2O_sys, T, eps_m_plot, cmap=cmap, vmin=0, vmax=1.1, shading='auto')
cb = fig.colorbar(pcm, ax=ax, ticks=np.arange(0, 1.1, 0.1))
cb.set_label("Melt Fraction")
ax.contour(H2O_sys, T, eps_f, levels=[1e-4], colors='k', linewidths=2)
cs = ax.contour(H2O_sys, T, rhob, levels=levels, colors='k')
ax.clabel(cs, inline=True, fontsize=7)

# Overlay the real alphaMELTS trajectory (requires Part A's `df`)
# Need a "total system H2O" value for each step to place it on this axis --
# if your alphaMELTS run was closed-system, system H2O is just your bulk
# input value (constant); if open-system/degassing, you'd need the
# per-step total H2O from your run's bulk composition output.
total_H2O_per_step = df["H2O_melt"]  # placeholder: replace with true
                                       # system-H2O-per-step if available
ax.plot(total_H2O_per_step, df["T_C"], '-wo', lw=2, ms=4,
        markerfacecolor='red', label="Real alphaMELTS path")
ax.legend()

ax.set_xlabel("Total System H2O wt%")
ax.set_ylabel("Temperature (°C)")
ax.set_title(f"{cfg['name']} parameter space with real alphaMELTS trajectory")
plt.tight_layout()
plt.show()
```

**One caveat on Part C:** the x-axis of the Part B map is *total system* water (`H2O_sys`), not dissolved melt water (`H2O_melt`) — these are the same only until saturation. If your alphaMELTS run is closed-system, total system water is just your fixed input bulk H2O value (so every point on the trajectory sits at a single x-coordinate, moving only vertically in T). I used `H2O_melt` above as a placeholder since that's what `AlphaMeltsStep` carries — you'll want to substitute the actual constant (or evolving, if open-system) total system water value from your run setup for a correct overlay.

---

## Summary of what's faithfully ported vs. adapted

| MATLAB element | Status |
|---|---|
| Case study configs (w, T, P, rhoh_fixed, c, labflag, etc.) | Transcribed exactly |
| `sigm`, `sigb`, `phi` grid computations | Faithful translation |
| Figure 1 (3-panel) | Faithful, matplotlib equivalent |
| Figure 2 (MELTS coupling map) | Faithful, including the masking/post-processing logic (with the comment/logic discrepancy flagged) |
| Figure 3 (volatile resistivity vs T) | Faithful |
| Fixed-resistivity-contour min/max melt extent (`InterX`-based) | **Not ported** — flagged as a follow-up if needed |
| Real alphaMELTS trajectory integration (Part A, C) | New capability, not in the original MATLAB — built to answer your actual question about linking live MELTS output |

As always: before trusting any plotted numbers, it's worth spot-checking a value or two against the actual published Cordell et al. (2022) figures, since neither of us can verify a translation's correctness without that kind of ground truth.