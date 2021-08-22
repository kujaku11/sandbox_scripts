# -*- coding: utf-8 -*-
"""
Created on Thu Jan 26 17:14:04 2017

@author: jpeacock
"""
import os
import mtpy.imaging.mtplot as mtplot

ga_dir = r"d:\Peacock\MTData\sev\Folsom_edi_original"
birrp_dir = r"d:\Peacock\MTData\sev\EDI_Files_birrp\Edited"


for ga_fn in os.listdir(ga_dir):
    for birrp_fn in os.listdir(birrp_dir):
        if birrp_fn[0:-4] in ga_fn:
            fn_list = [os.path.join(ga_dir, ga_fn), os.path.join(birrp_dir, birrp_fn)]

            pmr = mtplot.plot_multiple_mt_responses(
                fn_list=fn_list, plot_style="compare", plot_tipper="yr"
            )
            pmr.fig.savefig(
                os.path.join(birrp_dir, "{0}_compare.png".format(birrp_fn[0:-4])),
                dpi=600,
            )
            mtplot.plotnresponses.plt.close("all")
            break
