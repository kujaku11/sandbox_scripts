# -*- coding: utf-8 -*-
"""
Created on Tue Feb 17 17:37:19 2015

@author: jpeacock-pr
"""
from pathlib import Path
import mtpy.utils.array2raster as a2r

#model_fn = r"c:\Users\jpeacock\Documents\Geothermal\GraniteSprings\modem_inv\inv_02_tip\gs_prm_err03_tip02_cov03_NLCG_129.rho"
model_fn = Path(r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GraniteSprings\modem_inv\inv_03\gsv_z03_t02_c03_137.rho")
save_path = model_fn.parent.joinpath("depth_slices")

model_center = (-118.927443, 40.227213)


def check_dir(directory_path):
    if directory_path.is_dir() is False:
        directory_path.mkdir()
        print("Made directory {0}".format(directory_path))


check_dir(save_path)

modem_raster = a2r.ModEM_to_Raster()
modem_raster.model_obj.read_model_file(model_fn)

modem_raster.save_path = save_path
modem_raster.projection = "WGS84"
modem_raster.rotation_angle = 0.0
modem_raster.pad_east = 8
modem_raster.pad_north = 8
ll = modem_raster.get_model_lower_left_coord(model_center=model_center[::-1])
modem_raster.lower_left_corner = [ll[0] + .902, ll[1] + .53]
modem_raster.pad_east = 8
modem_raster.pad_north = 8
modem_raster.write_raster_files()
