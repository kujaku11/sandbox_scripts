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
    r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\Reports\phase3\figures"
)

### Open MTH5 file
mc = MTCollection()
mc.open_collection(
    filename=r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\cec_geysers_monitoring_ss_04.h5"
)
# =============================================================================
ptype = "pseudo"
survey_01 = "GZ2021"
survey_02 = "GZ2022"

ne_profile = (-122.8703335, 38.8077059, -122.7824293, 38.8775712)
nw_profile = (-122.8571019, 38.8558099, -122.7051194, 38.7548775)
utm_epsg = 32610

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
        mc.master_dataframe.survey == survey_01
    ]
    phase_1_list = mc.to_mt_data()

    mc.working_dataframe = mc.master_dataframe.loc[
        mc.master_dataframe.survey == survey_02
    ]
    phase_2_list = mc.to_mt_data()

    ptm = mc.plot_residual_phase_tensor(
        phase_1_list,
        phase_2_list,
        ellipse_size=0.0175,
        ellipse_range=(0, 20),
        med_filt_kernel=(7, 3),
        image_file=image_dict["file"],
        image_extent=image_dict["extent"],
        plot_freq=1.0 / 10,
        subplot_top=0.93,
        subplot_left=0.1,
    )

    for freq in [0.1]:  # , 1, 3, 7, 10, 20, 30, 50, 70, 100, 200, 300]:
        ptm.plot_freq = 1.0 / freq
        ptm.plot()

        ptm.save_plot(
            save_path.joinpath(f"rpt_{survey_01}_vs_{survey_02}_{freq}s.png"),
            fig_dpi=300,
        )


elif ptype == "pseudo":
    mc.working_dataframe = mc.master_dataframe.loc[
        mc.master_dataframe.survey == survey_01
    ]
    md1 = mc.to_mt_data()
    mc.working_dataframe = mc.master_dataframe.loc[
        mc.master_dataframe.survey == survey_02
    ]
    md2 = mc.to_mt_data()

    md1.utm_epsg = utm_epsg
    md2.utm_epsg = utm_epsg

    for line, fn in zip(
        [ne_profile, nw_profile],
        ["ne_profile_rpt_ps.png", "nw_profile_rpt_ps.png"],
    ):
        md1_profile = md1.get_profile(*line, 750)
        md1_profile.remove_station("gz201", "GZ2021")
        md1_profile.remove_station("gz332", "GZ2021")

        md2_profile = md2.get_profile(*line, 750)
        md2_profile.remove_station("gz2072", "GZ2023")
        md2_profile.remove_station("gz3062", "GZ2023")
        md2_profile.remove_station("gz3102", "GZ2023")

        if survey_01 == "GZ2017":
            md2_profile.remove_station("gz202", "GZ2023")
            md2_profile.remove_station("gz207", "GZ2023")
            md2_profile.remove_station("gz208", "GZ2023")
            md2_profile.remove_station("gz210", "GZ2023")
            md2_profile.remove_station("gz213", "GZ2023")
            md2_profile.remove_station("gz215", "GZ2023")

            md1_profile.remove_station("gz305", "GZ2017")
            md1_profile.remove_station("gz332", "GZ2017")

        pts = mc.plot_residual_phase_tensor(
            md1_profile,
            md2_profile,
            plot_type="ps",
            ellipse_range=(0, 25),
            med_filt_kernel=(7, 3),
            x_stretch=100,
            y_stretch=10000000,
            ellipse_size=4000000,
            station_id=(2, 6),
        )

        pts.save_plot(
            save_path.joinpath(f"{survey_01}_v_{survey_02}_{fn}"), fig_dpi=300
        )

mc.close_collection()
