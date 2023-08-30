# -*- coding: utf-8 -*-
"""
Created on Tue Aug 29 16:05:35 2023

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
from pathlib import Path
import numpy as np
from mtpy import MTCollection
from mtpy.modeling import StructuredGrid3D

# =============================================================================
edi_path = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\MTData\BV2023\EDI_Files_aurora\edited\GeographicNorth"
)
mc_path = edi_path.joinpath("bv2023.h5")

with MTCollection() as mc:
    if mc_path.exists():
        mc.open_collection(mc_path)
    else:
        mc.open_collection(mc_path)
        mc.add_tf(mc.make_file_list(edi_path))
        mc.add_tf(
            r"c:\Users\jpeacock\OneDrive - DOI\EDI_FILES\USArray.NVO09.2010.edi"
        )
    mc.working_dataframe = mc.master_dataframe
    md = mc.to_mt_data()


md.utm_epsg = 32611


md.interpolate(np.logspace(np.log10(1.0 / 500), np.log10(6000), 23))

md.z_model_error.error_type = "eigen"
md.z_model_error.error_value = 3
md.t_model_error.error_value = 0.02
md["Transportable Array.NVO09"].latitude = 40.2224614
md["Transportable Array.NVO09"].longitude = -117.3270484


md.compute_relative_locations()
md.compute_model_errors()

md.to_modem_data(
    data_filename=r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\BuffaloValley\modem_inv\inv_01\bv_modem_data_z03_t02.dat"
)
