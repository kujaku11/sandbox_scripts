from pathlib import Path
from mtpy import MTData
from mtpy.modeling.plots.plot_model_responses import PlotResponse

data_fn = Path(r"c:\Users\jpeacock\OneDrive - DOI\ClearLake\modem_inv\clvf_tests\cl_modem_data_z03_t02_tec_11.dat")
resp_fn = Path(r"c:\Users\jpeacock\OneDrive - DOI\ClearLake\modem_inv\clvf_tests\clvf_z03_t02_c02_smavg_042.dat")

pr = PlotResponse(
        data_fn=data_fn,
        resp_fn=resp_fn,
        plot_style=1,
        fig_size=[9, 3.25],
        ms=2,
        subplot_bottom=0.12,
        subplot_left=0.05,
        font_size=5.7,
        plot_z=False,
        cted=(0, 0, 0),
        ctmd=(0, 0, 0),
        ctem=(0.75, 0.0, 0.0),
        ctmm=(0.75, 0.0, 0.0),
        mted="o",
        mtem="x",
        mtmm="x",
        subplot_wspace=0.20,
    )

pr.plot_station = "cl435"

sv_path = Path(r"c:\Users\jpeacock\OneDrive - DOI\ClearLake\jvgr_manuscript\Figures\supplemental")
for ss in [s.split("/")[-1] for s in pr.data_object.station_paths if "data" in s]:
    pr.plot_station = ss
    pr.plot_tipper = True
    pr.plot()
    pr.save_figure(
        save_fn=sv_path / f"Supp_{ss}.png",
        file_format=None,
        fig_dpi=300,
        close_fig="y",
    )