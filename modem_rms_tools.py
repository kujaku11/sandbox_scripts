# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 10:59:30 2017

@author: jpeacock
"""

import numpy as np
import mtpy.modeling.modem as modem
import pandas as pd
import matplotlib.pyplot as plt


def get_rms_summary_df(res_obj, rms_thresh=5.0):
    """
    write summary files
    """
    keys = [
        "station",
        "lat",
        "lon",
        "z",
        "t",
        "zxx",
        "zxy",
        "zyx",
        "zyy",
        "tx",
        "ty",
        "notes",
    ]
    rms_dict = dict([(key, []) for key in keys])
    for r_arr in res_obj.data_array:
        r_arr["z"][np.where(r_arr["z"]) == 0] = np.nan
        r_arr["z_err"][np.where(r_arr["z"]) == 0] = np.nan
        r_arr["tip"][np.where(r_arr["tip"]) == 0] = np.nan
        r_arr["tip_err"][np.where(r_arr["tip"]) == 0] = np.nan

        z_rms = np.nanmean(r_arr["z"].__abs__() / r_arr["z_err"].real, axis=0)
        t_rms = np.nanmean(r_arr["tip"].__abs__() / r_arr["tip_err"].real, axis=0)

        if np.any(z_rms > rms_thresh) or np.any(t_rms > rms_thresh):
            notes = "***CHECK***"
            print("  --> check {0}".format(r_arr["station"]))
        else:
            notes = ""

        rms_list = [
            r_arr["station"],
            r_arr["lat"],
            r_arr["lon"],
            z_rms.mean(),
            t_rms.mean(),
            z_rms[0, 0],
            z_rms[0, 1],
            z_rms[1, 0],
            z_rms[1, 1],
            t_rms[0, 0],
            t_rms[0, 1],
            notes,
        ]
        for key, rms_value in zip(keys, rms_list):
            rms_dict[key].append(rms_value)

    df = pd.DataFrame(rms_dict, index=rms_dict["station"])

    return df


def get_rms_by_period_df(res_obj, rms_thresh=5.0):
    """
    get RMS by period
    """
    keys = ["{0:.1e}".format(period) for period in res_obj.period_list]
    comp_keys = ["z", "t", "zxx", "zxy", "zyx", "zyy", "tx", "ty"]
    rms_dict = dict([(ckey.lower(), []) for ckey in comp_keys])

    res_obj.data_array["z"][np.where(res_obj.data_array["z"]) == 0] = np.nan
    res_obj.data_array["z_err"][np.where(res_obj.data_array["z"]) == 0] = np.nan
    res_obj.data_array["tip"][np.where(res_obj.data_array["tip"]) == 0] = np.nan
    res_obj.data_array["tip_err"][np.where(res_obj.data_array["tip"]) == 0] = np.nan
    for ii, key in enumerate(keys):
        z_rms = np.nanmean(
            res_obj.data_array[ii]["z"].__abs__()
            / res_obj.data_array[ii]["z_err"].real,
            axis=0,
        )
        t_rms = np.nanmean(
            res_obj.data_array[ii]["tip"].__abs__()
            / res_obj.data_array[ii]["tip_err"].real,
            axis=0,
        )

        rms_list = [
            z_rms.mean(),
            t_rms.mean(),
            z_rms[0, 0],
            z_rms[0, 1],
            z_rms[1, 0],
            z_rms[1, 1],
            t_rms[0, 0],
            t_rms[0, 1],
        ]
        for ckey, rms_value in zip(comp_keys, rms_list):
            rms_dict[ckey].append(rms_value)

    df = pd.DataFrame(rms_dict, index=keys)

    return df


def plot_rms_summary(
    res_obj,
    ylim=(0, 5),
    bar_width=0.5,
    keys=["z", "t", "zxx", "zxy", "zyx", "zyy", "tx", "ty"],
):
    """
    plot summary as bar plots 
    """
    summary_df = get_rms_summary_df(res_obj)
    ax_list = summary_df[keys].plot.bar(
        width=bar_width, subplots=True, ylim=ylim, grid=True
    )
    for ax in ax_list:
        ax.set_axisbelow(True)
        ax.set_yticks(np.arange(ylim[0], ylim[1]))
        ax.set_title("")
        ax.legend(loc="upper right")
        ax.set_ylabel("RMS")

    fig = plt.gcf()
    fig.set_size_inches([8, 9.5])
    fig.tight_layout()
    return fig, ax_list


def plot_rms_by_period(
    res_obj,
    ylim=(0, 5),
    bar_width=0.5,
    keys=["z", "t", "zxx", "zxy", "zyx", "zyy", "tx", "ty"],
):
    """
    plot periods as bar plots 
    """
    period_df = get_rms_by_period_df(res_obj)
    ax_list = period_df[keys].plot.bar(
        width=bar_width, subplots=True, ylim=ylim, grid=True
    )
    for ax in ax_list:
        ax.set_axisbelow(True)
        ax.set_yticks(np.arange(ylim[0], ylim[1]))
        ax.set_title("")
        ax.legend(loc="upper right")
        ax.set_ylabel("RMS")
    ax_list[-1].set_xlabel("Period (s)")

    fig = plt.gcf()
    fig.set_size_inches([8, 9.5])
    fig.tight_layout()
    return fig, ax_list


# =============================================================================
# run things
# =============================================================================
# res_fn = r"c:\Users\jpeacock\OneDrive - DOI\Geysers\modem_inv\inv03\gz_err03_cov02_NLCG_057.res"
# res_fn = r"c:\Users\jpeacock\OneDrive - DOI\Geysers\modem_inv\inv04\gz_rm50_z03_c02_104.res"
# res_fn = r"c:\Users\jpeacock\OneDrive - DOI\Geysers\gz_z03_c02_074.res"
res_fn = (
    r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GabbsValley\modem_inv\st_topo_inv_02\st_z05_t02_c03_pfa_108.res"
)
rms_thresh = 7.0

res_obj = modem.Data()
res_obj.read_data_file(res_fn)

summary_df = get_rms_summary_df(res_obj)
period_df = get_rms_by_period_df(res_obj)

ax1 = plot_rms_summary(res_obj, keys=["z", "zxx", "zxy", "zyx", "zyy", "t", "tx", "ty"])
ax2 = plot_rms_by_period(res_obj, keys=["z", "zxx", "zxy", "zyx", "zyy", "t", "tx", "ty"])
