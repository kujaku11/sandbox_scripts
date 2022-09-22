# -*- coding: utf-8 -*-
"""
Created on Thu Jan 13 10:11:52 2022

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
from pathlib import Path
from mtpy import MTCollection

# =============================================================================
save_path = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\Reports\phase2\figures"
)

### Open MTH5 file
mc = MTCollection()
mc.open_collection(
    filename=r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\cec_geysers_monitoring_ss.h5"
)
# =============================================================================
ptype = "map"

if ptype == "map":
    image_dict = {
        "file": r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\Reports\figures\basemap_no_stations.png",
        "extent": (-122.9015, -122.67, 38.9025, 38.7175),
    }

    # image_dict = {
    #     "file": r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\calpine_fault_planes.png",
    #     "extent": (-122.903, -122.6, 38.915, 38.655),
    # }

    mc.working_dataframe = mc.master_dataframe.loc[
        mc.master_dataframe.survey == "GZ2017"
    ]
    phase_1_list = mc.get_tf_list()

    mc.working_dataframe = mc.master_dataframe.loc[
        mc.master_dataframe.survey == "GZ2022"
    ]
    phase_2_list = mc.get_tf_list()

    ptm = mc.plot_residual_phase_tensor(
        phase_1_list,
        phase_2_list,
        ellipse_size=0.0175,
        ellipse_range=(0, 20),
        med_filt_kernel=(7, 3),
        image_dict=image_dict,
        plot_freq=1.0 / 10,
        subplot_top=0.93,
        subplot_left=0.1,
    )

    for freq in [0.1, 1, 3, 7, 10, 20, 30, 50, 70, 100, 200, 300]:
        ptm.plot_freq = 1.0 / freq
        ptm.plot()

        ptm.save_plot(
            save_path.joinpath(f"rpt_2017_vs_2022_{freq}s.png"),
            fig_dpi=300,
        )

# elif ptype == "pseudo":
#     profile_index = [25, 26, 28, 10, 9, 8, 7, 6, 38, 40, 39]
#     list_01 = df.original.iloc[profile_index].to_list()
#     list_02 = df.phase_01_ss.iloc[profile_index].to_list()

#     ps = mtplot.plot_residual_pt_ps(
#         list_01, list_02, med_filt_kernel=(7, 3), plot_yn="n"
#     )
#     ps.ellipse_range = (0, 20)
#     ps.ellipse_size
