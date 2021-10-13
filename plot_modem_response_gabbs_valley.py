# -*- coding: utf-8 -*-
"""
Created on Mon Mar 02 11:58:23 2015

@author: jpeacock-pr
"""

import mtpy.modeling.modem as modem
import os

dfn = r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GabbsValley\modem_inv\st_topo_inv_02\gv_modem_data_z05_t03.dat"
rfn = r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GabbsValley\modem_inv\st_topo_inv_02\st_z05_t02_c025_126.dat"
sv_path = r"c:\Users\jpeacock\OneDrive - DOI\General\manuscript\grl_tex\supplementary"

plot_type = ["response"]
file_fmt = 'pdf"'


data_obj = modem.Data()
data_obj.read_data_file(dfn)


station_list = data_obj.station_locations.station.copy()

if "maps" in plot_type:
    pm = modem.PlotRMSMaps(
        rfn[:-4] + ".res",
        marker="o",
        save_path=sv_path,
        fig_size=[4.725, 4.64],
        subplot_right=0.875,
        subplot_top=0.93,
        tick_locator=0.3,
    )
    pm.plot_loop(fig_format=file_fmt)

if "response" in plot_type:
    pr = modem.PlotResponse(
        data_fn=dfn,
        resp_fn=rfn,
        plot_type=station_list[0],
        fig_size=[11, 3.25],
        ms=2,
        subplot_bottom=0.12,
        subplot_left=0.075,
        font_size=5.7,
        plot_z=False,
        cted=(0, 0, 0),
        ctmd=(0, 0, 0),
        ctem=(0.75, 0.0, 0.0),
        ctmm=(0.75, 0.0, 0.0),
        mted="o",
        mtem="x",
        mtmm="x",
        subplot_wspace=0.25,
    )

    pr.legend_pos = (0.5, 1.225)
    for ss in station_list:
        pr.plot_type = ss
        pr.redraw_plot()

        pr.save_figure(
            save_fn=os.path.join(sv_path, "Supp_{0}_resp.pdf".format(ss)), fig_dpi=300
        )

    lines = []
    for ii in range(0, data_obj.station_locations.station.size - 2, 3):
        s1 = data_obj.station_locations.station[ii]
        s2 = data_obj.station_locations.station[ii + 1]
        s3 = data_obj.station_locations.station[ii + 2]

        lines.append(r"\begin{picture}(1, 1)")
        gline = r"\put(0,-212){\includegraphics[width=.92\textwidth]{"
        gline += "Supp_{0}_resp.pdf".format(s1)
        gline += r"}}"
        lines.append(gline)

        gline = r"\put(0,-425){\includegraphics[width=.92\textwidth]{"
        gline += "Supp_{0}_resp.pdf".format(s2)
        gline += r"}}"
        lines.append(gline)

        gline = r"\put(0,-640){\includegraphics[width=.92\textwidth]{"
        gline += "Supp_{0}_resp.pdf".format(s3)
        gline += r"}}"
        lines.append(gline)
        lines.append(r"\end{picture}")
        lines.append(r"\newpage")
        lines.append("")

    with open(os.path.join(sv_path, "figure_lines.txt"), "w") as fid:
        fid.write("\n".join(lines))
