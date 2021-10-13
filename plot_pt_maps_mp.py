# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 12:09:27 2021

:copyright: 
    Jared Peacock (jpeacock@usgs.gov)

:license: MIT

"""

from pathlib import Path
from mtpy.imaging import mtplot

edi_path = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\MountainPass\modem_inv\inv_07\new_edis"
)
edi_list = list(edi_path.glob("*.edi"))

geo_tiff = r"c:\Users\jpeacock\OneDrive - DOI\MountainPass\gis\map11_mtn_pass_merged_mag_rtp_geo_projected.tif"

ptm = mtplot.plot_pt_map(
    fn_list=edi_list,
    background_image=geo_tiff,
    ellipse_size=0.02,
    xpad=0.001,
    ypad=0.001,
)

ptm.plot()
