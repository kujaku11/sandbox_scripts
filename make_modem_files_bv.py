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
from mtpy import MTCollection, MTData
from mtpy.modeling import StructuredGrid3D
from mtpy.modeling.modem import Covariance

# =============================================================================

dfn = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\BuffaloValley\modem_inv\inv_02\bv_modem_data_z03_t02_tls_01.dat"
)
topo_fn = r"c:\Users\jpeacock\OneDrive - DOI\ArcGIS\westcoast_etopo.asc"

# =============================================================================
# Make data file
# =============================================================================
if not dfn.exists():
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
        md = mc.to_mt_md()

    md.utm_epsg = 32611

    md.interpolate(np.logspace(np.log10(1.0 / 500), np.log10(6000), 23))

    md.z_model_error.error_type = "eigen"
    md.z_model_error.error_value = 3
    md.t_model_error.error_value = 0.02
    md["Transportable Array.NVO09"].latitude = 40.2224614
    md["Transportable Array.NVO09"].longitude = -117.3270484

    md.compute_relative_locations()
    md.compute_model_errors()

    md.to_modem_md(md_filename=dfn.parent.joinpath("bv_modem_md_z03_t02.dat"))
else:
    md = MTData()
    md.from_modem(dfn)


# =============================================================================
# build model
# =============================================================================
mod_obj = StructuredGrid3D(
    station_locations=md.station_locations, center_point=md.center_point
)

mod_obj.cell_size_east = 500
mod_obj.cell_size_north = 500
mod_obj.pad_east = 7
mod_obj.pad_north = 7
mod_obj.pad_num = 4
mod_obj.ew_ext = 200000
mod_obj.ns_ext = 200000
mod_obj.z_mesh_method = "default"
mod_obj.z_bottom = 200000
mod_obj.z_target_depth = 70000
mod_obj.pad_z = 5
mod_obj.n_air_layers = 25
mod_obj.n_layers = 90
mod_obj.z1_layer = 25
mod_obj.pad_stretch_v = 1.85
mod_obj.z_layer_rounding = 1
mod_obj.res_initial_value = 50

mod_obj.make_mesh()
mod_obj.add_topography_to_model(
    topography_file=topo_fn, max_elev=1930, airlayer_type="constant"
)

md.center_stations(mod_obj)
md.project_stations_on_topography(mod_obj)
md.to_modem(dfn.parent.joinpath(f"{dfn.stem}_topo.dat"))
mod_obj.station_locations = md.station_locations

mod_obj.plot_mesh()

mod_obj.to_modem(
    save_path=dfn.parent,
    model_fn_basename="bv_sm02_topo.rho",
)


cov = Covariance(grid_dimensions=mod_obj.res_model.shape)
cov.smoothing_east = 0.5
cov.smoothing_north = 0.5
cov.smoothing_z = 0.5
cov.smoothing_num = 1

cov.write_covariance_file(
    dfn.parent.joinpath("covariance.cov"),
)
