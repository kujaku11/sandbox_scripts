import panel as pn
import numpy as np
from bokeh.plotting import figure
from bokeh.models import HoverTool

from .melt_physics_workflow import (
    build_default_models,
    JointMeltEstimator,
)
from .alphamelts_io import AlphaMELTSLoader

pn.extension()

melt_cond, archie, elastic, seismic = build_default_models()
estimator = JointMeltEstimator(melt_cond, archie, elastic, seismic)

# Widgets
run_folder = pn.widgets.TextInput(name="alphaMELTS run folder", value=".")
status = pn.pane.Str("")
step_picker = pn.widgets.IntSlider(name="Equilibrium step index", start=0, end=0, value=0)

T_K = pn.widgets.FloatSlider(name="Temperature (K)", start=1000, end=1800, step=10, value=1473)
H2O = pn.widgets.FloatSlider(name="Melt H2O (wt%)", start=0.0, end=8.0, step=0.1, value=2.0)
CO2 = pn.widgets.FloatSlider(name="Melt CO2 (wt%)", start=0.0, end=3.0, step=0.05, value=0.2)

C = pn.widgets.FloatSlider(name="Archie C", start=0.3, end=1.2, step=0.05, value=archie.C)
n = pn.widgets.FloatSlider(name="Archie n", start=0.8, end=2.5, step=0.05, value=archie.n)
phi_c = pn.widgets.FloatSlider(name="Percolation threshold φc", start=0.0, end=0.05, step=0.001, value=archie.phi_c)
sigma_solid = pn.widgets.FloatInput(name="Solid σ (S/m)", value=archie.sigma_solid_S, step=0.001)

K = pn.widgets.FloatInput(name="Solid K (GPa)", value=elastic.K/1e9, step=1.0)
G = pn.widgets.FloatInput(name="Solid G (GPa)", value=elastic.G/1e9, step=1.0)
rho = pn.widgets.FloatInput(name="Solid ρ (kg/m3)", value=elastic.rho, step=10.0)

a_vp = pn.widgets.FloatSlider(name="a_vp", start=0.5, end=2.5, step=0.05, value=seismic.a_vp)
a_vs = pn.widgets.FloatSlider(name="a_vs", start=1.0, end=4.0, step=0.05, value=seismic.a_vs)

target_rho = pn.widgets.FloatInput(name="Target ρ_bulk (Ω·m)", value=5.0, step=0.1)
target_vp = pn.widgets.FloatInput(name="Target Vp (m/s)", value=7000.0, step=10.0)
phi_max = pn.widgets.FloatSlider(name="Max φ", start=0.05, end=0.40, step=0.01, value=0.20)

def update_models():
    archie.C = C.value
    archie.n = n.value
    archie.phi_c = phi_c.value
    archie.sigma_solid_S = sigma_solid.value
    elastic.K = K.value * 1e9
    elastic.G = G.value * 1e9
    elastic.rho = rho.value
    seismic.a_vp = a_vp.value
    seismic.a_vs = a_vs.value

def make_curves():
    update_models()
    comp = {"H2O": H2O.value, "CO2": CO2.value}
    phis = np.linspace(0.0, phi_max.value, 201)
    results = [estimator.forward(phi, T_K.value, comp) for phi in phis]
    return phis, results

def plots_and_inversion():
    phis, results = make_curves()
    rho_bulk = np.array([r["rho_bulk_Ohm_m"] for r in results])
    vp = np.array([r["vp_ms"] for r in results])

    p1 = figure(height=300, width=450, title="Bulk resistivity vs melt fraction φ",
                x_axis_label="φ", y_axis_label="ρ_bulk (Ω·m)")
    p1.line(phis, rho_bulk, line_width=3, color="navy")
    p1.add_tools(HoverTool(tooltips=[("φ", "@x{0.000}"), ("ρ (Ω·m)", "@y{0.00}")]))
    p1.line([phis[0], phis[-1]], [target_rho.value, target_rho.value],
            line_color="red", line_dash="dashed", legend_label="Target ρ")

    p2 = figure(height=300, width=450, title="P-wave velocity vs melt fraction φ",
                x_axis_label="φ", y_axis_label="Vp (m/s)")
    p2.line(phis, vp, line_width=3, color="green")
    p2.add_tools(HoverTool(tooltips=[("φ", "@x{0.000}"), ("Vp", "@y{0.}")]))
    p2.line([phis[0], phis[-1]], [target_vp.value, target_vp.value],
            line_color="red", line_dash="dashed", legend_label="Target Vp")

    comp = {"H2O": H2O.value, "CO2": CO2.value}
    inv = estimator.invert_phi(target_rho_bulk_Ohm_m=target_rho.value,
                               target_vp_ms=target_vp.value,
                               T_K=T_K.value, comp=comp,
                               phi_bounds=(0.0, phi_max.value))
    txt = pn.pane.Str(f"Best-fit φ = {inv['phi']:.3f}\n"
                      f"Predicted ρ_bulk = {inv['rho_bulk_Ohm_m']:.2f} Ω·m\n"
                      f"Predicted Vp = {inv['vp_ms']:.0f} m/s\n"
                      f"Misfit = {inv['misfit']:.3e}")
    return pn.Row(p1, p2), txt

curves, inv_txt = plots_and_inversion()

# alphaMELTS IO hooks
def load_run():
    global loader
    try:
        loader = AlphaMELTSLoader(run_folder.value)
        steps = loader.load()
        if not steps:
            step_picker.end = 0
            status.object = "No steps parsed. Check files."
            return
        step_picker.end = len(steps)-1
        status.object = f"Loaded {len(steps)} steps."
    except Exception as e:
        status.object = f"Error: {e}"

def apply_step():
    idx = step_picker.value
    ms = loader.to_melts_state(idx)
    T_K.value = ms.temperature_K
    H2O.value = ms.melt_composition.get("H2O", 0.0)
    CO2.value = ms.melt_composition.get("CO2", 0.0)
    return pn.pane.Str(f"MELTS φ (thermo) = {ms.melt_fraction:.3f}")

apply_info = pn.pane.Str("")

@pn.depends(run_folder, watch=True)
def refresh_run_folder(_=None):
    load_run()

@pn.depends(step_picker, watch=True)
def refresh_step(_=None):
    global apply_info
    apply_info.object = apply_step().object

@pn.depends(T_K, H2O, CO2, C, n, phi_c, sigma_solid, K, G, rho, a_vp, a_vs, target_rho, target_vp, phi_max, watch=True)
def refresh_plots(_=None):
    new_plots, txt = plots_and_inversion()
    return pn.Column(new_plots, txt)

controls = pn.WidgetBox(
    "## alphaMELTS IO",
    run_folder, status, step_picker, apply_info,
    "# MELT & ELECTRICAL",
    T_K, H2O, CO2, C, n, phi_c, sigma_solid,
    "# ELASTIC & SEISMIC",
    K, G, rho, a_vp, a_vs,
    "# TARGETS",
    target_rho, target_vp, phi_max
)

app = pn.Row(controls, pn.Spacer(width=10), refresh_plots)
app.servable(title="Melt Fraction Estimator (Archie + Vp)")