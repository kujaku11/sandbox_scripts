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
    r"c:\Users\jpeacock\OneDrive - DOI\MIST\modem_inv\inv_03\mist_modem_data_big_05.dat"
)

# topo_fn = r"c:\Users\jpeacock\OneDrive - DOI\ArcGIS\westcoast_etopo.asc"
topo_fn = r"c:\Users\jpeacock\OneDrive - DOI\western_us.tiff"

utm_epsg = 32611
survey = "mist"

# =============================================================================
# Make data file
# =============================================================================
if not dfn.exists():
    edi_path = Path(r"c:\Users\jpeacock\OneDrive - DOI\MIST\processed_edis")
    mc_path = dfn.parent.joinpath("mist_tf.h5")

    with MTCollection() as mc:
        if mc_path.exists():
            mc.open_collection(mc_path)
        else:
            mc.open_collection(mc_path)
            mc.add_tf(mc.make_file_list(edi_path))
        mc.working_dataframe = mc.master_dataframe
        md = mc.to_mt_data()

    md.utm_epsg = utm_epsg

    md.interpolate(np.logspace(np.log10(1.0 / 300), np.log10(6000), 23))

    md.z_model_error.error_type = "eigen"
    md.z_model_error.error_value = 3
    md.t_model_error.error_value = 0.02

    md.compute_relative_locations()
    md.compute_model_errors()

    md.to_modem(md_filename=dfn.parent.joinpath(f"{survey}_modem_z03_t02.dat"))
else:
    md = MTData()
    md.from_modem(dfn)
    md._center_lat = None
    md._center_lon = None
    md.compute_relative_locations()


# =============================================================================
# build model
# =============================================================================
mod_obj = StructuredGrid3D(
    station_locations=md.station_locations, center_point=md.center_point
)

mod_obj.cell_size_east = 1500
mod_obj.cell_size_north = 1500
mod_obj.pad_east = 10
mod_obj.pad_north = 10
mod_obj.pad_num = 5
mod_obj.ew_ext = 400000
mod_obj.ns_ext = 400000
mod_obj.z_mesh_method = "default"
mod_obj.z_bottom = 600000
mod_obj.z_target_depth = 200000
mod_obj.pad_z = 6
mod_obj.n_air_layers = 25
mod_obj.n_layers = 110
mod_obj.z1_layer = 25
mod_obj.pad_stretch_v = 1.6
mod_obj.z_layer_rounding = 1
mod_obj.res_initial_value = 30

mod_obj.make_mesh()
mod_obj.add_topography_to_model(
    topography_file=topo_fn,
    max_elev=800,
    airlayer_type="constant",
    shift_east=0,
    shift_north=0,
)

md.center_stations(mod_obj)
md.project_stations_on_topography(mod_obj)
md.to_modem(dfn.parent.joinpath(f"{dfn.stem}_topo.dat"))
md.z_model_error.error_value = 10
md.z_model_error.error_type = "eigen"
md.t_model_error.error_value = 0.03

md.to_modem(dfn.parent.joinpath(f"{survey}_modem_data_z10.dat"), inv_mode="2")
md.to_modem(dfn.parent.joinpath(f"{survey}_modem_data_t03.dat"), inv_mode="5")


mod_obj.station_locations = md.station_locations
mod_obj.plot_mesh()

mod_obj.to_modem(
    save_path=dfn.parent,
    model_fn_basename="mist_sm30_topo.rho",
)


cov = Covariance(grid_dimensions=mod_obj.res_model.shape)
cov.smoothing_east = 0.5
cov.smoothing_north = 0.5
cov.smoothing_z = 0.3
cov.smoothing_num = 1

cov.write_covariance_file(
    dfn.parent.joinpath("covariance_topo.cov"), res_model=mod_obj.res_model
)
