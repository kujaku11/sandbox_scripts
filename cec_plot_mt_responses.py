# -*- coding: utf-8 -*-
"""
Created on Thu Sep 15 11:03:02 2022

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
from pathlib import Path
from mtpy import MTCollection

# =============================================================================
save_path = Path(
    r"c:\\Users\\jpeacock\\OneDrive - DOI\\Geysers\\CEC\\Reports\\phase2\\figures"
)

### Open MTH5 file
mc = MTCollection()
mc.open_collection(
    filename=r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\cec_geysers_monitoring_ss.h5"
)


# create a list of station to iterate over focused on repeat stations with
# 2022
station_list = mc.master_dataframe.loc[
    mc.master_dataframe.survey == "GZ2022"
].tf_id.unique()

# plot the responses
for tf_id in station_list:
    station_df = mc.master_dataframe.loc[mc.master_dataframe.tf_id == tf_id]
    station_df = station_df.sort_values("survey")
    if tf_id in [
        "gz350",
        "gz215",
        "gz315",
        "gz318",
        "gz324",
        "gz325",
        "gz202",
        "gz203",
        "gz204",
        "gz206",
        "gz211",
        "gz214",
        "gz308",
        "gz311",
        "gz306",
        "gz320",
    ]:
        res_limits = (1, 10000)
        phase_limits = (0, 104)
    elif tf_id in ["gz348", "gz205", "gz212"]:

        res_limits = (0.1, 30000)
        phase_limits = (0, 200)

    elif tf_id in ["gz331", "gz327"]:
        res_limits = (0.01, 10000)
        phase_limits = (0, 104)

    else:
        res_limits = (0.3, 1000)
        phase_limits = (0, 104)

    pmr = mc.plot_mt_response(
        station_df,
        plot_style="compare",
        lw=0.75,
        plot_pt=True,
        marker_size=1.5,
        res_limits=res_limits,
        phase_limits=phase_limits,
    )
    pmr.save_plot(
        save_path.joinpath(f"{tf_id}_compare.png"),
        fig_dpi=300,
    )
