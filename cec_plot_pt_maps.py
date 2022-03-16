# -*- coding: utf-8 -*-
"""
Created on Thu Jan 13 10:11:52 2022

@author: jpeacock
"""

import pandas as pd
from mtpy.imaging import mtplot


df_fn =r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\phase_01_filenames.csv"
df = pd.read_csv(df_fn)

ptype = "map"

if ptype == "map":
    # image_dict = {"file": r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\Reports\figures\basemap_no_stations.png",
    #               "extent": (-122.9015, -122.67, 38.9025, 38.7175)}
    
    image_dict = {"file": r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\calpine_fault_planes.png",
                  "extent": (-122.903, -122.6, 38.915, 38.655)}
    
    pr = mtplot.plot_residual_pt_maps(
        df.original.to_list(), 
        df.phase_01.to_list(),
        med_filt_kernel=(7, 3),
        image_dict=image_dict, 
        plot_freq=1./10, 
        plot_yn="n",
    )
    
    pr.ellipse_size = 0.0175
    pr.ellipse_range = (0, 20)
    
    for freq in [.1, 1, 10, 30, 100, 300]:
        pr.plot_freq = 1./freq
        pr.plot()
    
        pr.save_figure(f"c:\\Users\\jpeacock\\OneDrive - DOI\\Geysers\\CEC\\Reports\\figures\\rpt_map_fault_planes_{freq}s.png",
                       fig_dpi=300)
    
elif ptype == "pseudo":
    profile_index = [25, 26, 28, 10, 9, 8, 7, 6, 38, 40, 39]
    list_01 = df.original.iloc[profile_index].to_list()
    list_02 = df.phase_01_ss.iloc[profile_index].to_list()
    
    ps = mtplot.plot_residual_pt_ps(list_01, list_02, med_filt_kernel=(7, 3),
                                    plot_yn="n")
    ps.ellipse_range = (0, 20)
    ps.ellipse_size
    
    
        

