# -*- coding: utf-8 -*-
"""
Created on Mon Mar 02 11:58:23 2015

@author: jpeacock-pr
"""

import mtpy.modeling.modem_new as modem
import os

dfn = r"c:\MinGW32-xy\Peacock\ModEM\WS_StartingModel_03_tipper\mb_data_tipper.dat"
rfn = r"c:\MinGW32-xy\Peacock\ModEM\WS_StartingModel_03_tipper\cov3_mb_tipper_NLCG_028.dat"
sv_path = r"c:\Users\jpeacock-pr\Google Drive\JVG"

data_obj = modem.Data()
data_obj.read_data_file(dfn)

station_list = data_obj.station_locations["station"].copy()

pr = modem.PlotResponse(
    data_fn=dfn,
    resp_fn=rfn,
    plot_type=station_list[0],
    fig_size=[6, 3.25],
    ms=2,
    subplot_bottom=0.12,
    subplot_left=0.07,
    font_size=5.7,
    plot_yn="n",
)


for ss in station_list:
    pr.plot_type = ss
    pr.redraw_plot()

    pr.save_figure(
        save_fn=os.path.join(sv_path, "Supp_{0}_resp.pdf".format(ss)), fig_dpi=600
    )
