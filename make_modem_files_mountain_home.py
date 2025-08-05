# -*- coding: utf-8 -*-
"""
Created on Wed May 25 17:17:14 2016

@author: jpeacock
"""

from pathlib import Path
from mtpy import MTData
from mtpy.modeling import StructuredGrid3D
from mtpy.modeling.modem import Covariance, ModEMConfig

# ==============================================================================
# Inputs
# ==============================================================================
save_path = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\MountainHome\modem_inv\inv_02"
)
topo_fn = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\MountainHome\modem_inv\mh_topo.tif"
)
# fn_stem = "mh"
# s_edi_list = [
#     os.path.join(edi_path, ss)
#     for ss in os.listdir(edi_path)
#     if ss.endswith(".edi")
#     and "MHB" not in ss
#     and ss[0:4] not in ["MHW3", "MHW4", "MHW5"]
# ]

if not save_path.exists():
    save_path.mkdir()

dfn = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\MountainHome\modem_inv\inv_02\mh_modem_data_z03_t02_edit.dat"
)

# ==============================================================================
# Make the data file
# ==============================================================================
md = MTData()
md.from_modem(dfn)

# ==============================================================================
# First make the mesh
# ==============================================================================
mod_obj = StructuredGrid3D(
    station_locations=md.station_locations, center_point=md.center_point
)
mod_obj.cell_size_east = 100
mod_obj.cell_size_north = 100
mod_obj.pad_east = 10
mod_obj.pad_north = 10
mod_obj.ew_ext = 300000
mod_obj.ns_ext = 300000
mod_obj.z_bottom = 250000
mod_obj.z_target_depth = 50000
mod_obj.pad_z = 5
mod_obj.pad_num = 4
mod_obj.n_layers = 70
mod_obj.n_air_layers = 20
mod_obj.z1_layer = 10
mod_obj.z_mesh_method = "default"
mod_obj.pad_stretch_v = 1.85
mod_obj.z_layer_rounding = 1
mod_obj.res_initial_value = 150

# --> here is where you can rotate the mesh
mod_obj.mesh_rotation_angle = 0

mod_obj.make_mesh()
## There is basically no topography in the station area.
# mod_obj.add_topography_to_model(
#     topography_file=topo_fn,
#     max_elev=3375,
#     airlayer_type="constant",
#     shift_east=0,  # -1200,
# )

# md.center_stations(mod_obj)
md.project_stations_on_topography(mod_obj)
md.to_modem(dfn.parent.joinpath("mh_modem_data_z03_t02_tec.dat"))
mod_obj.station_locations = md.station_locations

mod_obj.plot_mesh()

mod_obj.to_modem(save_path.joinpath(f"mh_sm150.rho"))


# ==============================================================================
# make the covariance file
# ==============================================================================
cov = Covariance(grid_dimensions=mod_obj.res_model.shape)
cov.smoothing_east = 0.4
cov.smoothing_north = 0.4
cov.smoothing_z = 0.4
cov.smoothing_num = 1

cov.write_covariance_file(cov_fn=save_path.joinpath("covariance.cov"))
