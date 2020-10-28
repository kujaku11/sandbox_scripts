# -*- coding: utf-8 -*-
"""
Created on Mon Feb 06 14:22:56 2017

@author: jpeacock
"""

import os
import mtpy.imaging.mtplot as mtplot

edi_path = r"c:\Users\jpeacock\Documents\iMush\iMush_edited_edi_files_tipper_rot_geographic_north"
edi_list = [
    os.path.join(edi_path, edi) for edi in os.listdir(edi_path) if edi.endswith(".edi")
]

ptm = mtplot.plot_pt_map(
    fn_list=edi_list,
    plot_yn="n",
    ellipse_dict={"size": 0.0025},
    arrow_dict={"size": 0.09, "head_width": 0.01, "head_length": 0.01},
    image_dict={
        "file": r"c:\Users\jpeacock\Documents\iMush\imush_basemap_google_earth.jpg",
        "extent": (-123.738, -120.1438, 47.325, 45.5387),
    },
    plot_tipper="yri",
)

ptm.plot_freq = 7.1825e-3
ptm.ftol = 0.5
ptm.arrow_color_real = (0.85, 0.8, 0.1)
ptm.arrow_color_imag = (0.25, 0.25, 0.75)
ptm.arrow_lw = 0.5
ptm.fig_size = [5, 5]
ptm.plot()


for ff in [9.375000e-02, 7.812500e-03]:
    # for ff in [9.765600e-04]:
    ptm.plot_freq = ff
    ptm.redraw_plot()
    ptm.fig.savefig(
        r"c:\Users\jpeacock\Documents\iMush\imush_pt_map_{0:.0f}s_t_rot.png".format(
            1.0 / ff
        ),
        dpi=600,
    )
