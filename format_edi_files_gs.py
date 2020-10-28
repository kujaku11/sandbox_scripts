# -*- coding: utf-8 -*-
"""
Created on Wed Dec 06 15:50:19 2017

@author: jpeacock
"""
import os
import mtpy.core.mt as mt
import mtpy.imaging.plot_mt_response as pr
import mtpy.usgs.usgs_archive as archive
import numpy as np

# =============================================================================
# Inputs
# =============================================================================
dir_path = r"d:\Peacock\MTData\GraniteSprings\EDI_Files_birrp\Rotated_m13_deg"
cfg_fn = r"D:\Peacock\MTData\GraniteSprings\EDI_Files_birrp\granite_springs_birrp.cfg"
edi_path = r"d:\Peacock\MTData\GraniteSprings\EDI_Files_birrp\Rotated_m13_deg\Edited"
sv_path = os.path.join(dir_path, r"granite_springs_edi")
plot_sv_path = os.path.join(dir_path, "granite_springs_plots")

# =============================================================================
# Make any directories needed
# =============================================================================
def check_path(path):
    if not os.path.exists(path):
        os.mkdir(path)


for d_path in [sv_path, plot_sv_path]:
    check_path(d_path)

# =============================================================================
# Get list of EDI's
# =============================================================================
edi_list = [
    os.path.join(edi_path, edi) for edi in os.listdir(edi_path) if edi.endswith(".edi")
]

for edi in edi_list:

    mt_obj = mt.MT(edi)
    mt_obj.read_cfg_file(cfg_fn)
    mt_obj.elev = archive.get_nm_elev(mt_obj.lat, mt_obj.lon)
    new_freq = np.logspace(np.log10(0.00097752), np.log10(767.99), num=40)[::-1]
    mt_obj.Z, mt_obj.Tipper = mt_obj.interpolate(new_freq)

    p1 = mt_obj.plot_mt_response(plot_num=1, phase_limits=(0, 89))
    p1.save_plot(os.path.join(plot_sv_path, mt_obj.station + ".png"), fig_dpi=600)
    pr.plt.close("all")

    mt_obj.write_mt_file(save_dir=sv_path)
#    mt_obj.write_mt_file(save_dir=xml_sv_path, file_type='xml')
