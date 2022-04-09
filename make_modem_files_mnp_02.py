# -*- coding: utf-8 -*-
"""
Created on Mon Apr 25 17:20:17 2016

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
import os
from pathlib import Path
import numpy as np
import mtpy.modeling.modem as modem
import mtpy.core.mt as mt

# =============================================================================
# Parameters
# =============================================================================
edi_path = Path(r"c:\Users\jpeacock\OneDrive - DOI\EDI_Files")
avg_path = Path(r"c:\Users\jpeacock\OneDrive - DOI\MountainPass\modem_inv\mnp_avg_edis")
save_path = Path(r"c:\Users\jpeacock\OneDrive - DOI\MountainPass\modem_inv\mnp_03")
topo_fn = r"c:\Users\jpeacock\OneDrive - DOI\MusicValley\mv_topo.asc"

fn_stem = "mnp"

overwrite = False
topography = False


bounds = {"lat": np.array([34.3, 35.75]), "lon": np.array([-116.345, -114.75])}

dfn = save_path.joinpath("{0}_modem_data_z03_t02.dat".format(fn_stem))
if overwrite and dfn.exists():
    os.remove(dfn)

if not save_path.exists():
    save_path.mkdir()
# =============================================================================
# Get edi files
# =============================================================================
if not dfn.exists():
    edi_list = list(edi_path.glob("mnp*.edi")) + list(avg_path.glob("*.edi"))

# ==============================================================================
# Make the data file
# ==============================================================================
if not dfn.exists():
    inv_period_list = np.logspace(np.log10(1.0 / 300), np.log10(2000), num=23)
    data_obj = modem.Data(edi_list=edi_list, period_list=inv_period_list)
    data_obj.error_type_z = "eigen_floor"
    data_obj.error_value_z = 3.0
    data_obj.error_type_tipper = "abs_floor"
    data_obj.error_value_tipper = 0.02
    data_obj.inv_mode = "1"
    data_obj.model_epsg = 32611

    # --> here is where you can rotate the data
    data_obj.write_data_file(
        save_path=save_path,
        fn_basename="{0}_modem_data_z{1:02.0f}_t{2:02.0f}.dat".format(
            fn_stem, data_obj.error_value_z, 100 * data_obj.error_value_tipper
        ),
        fill=True,
        compute_error=True,
        elevation=False,
    )
else:
    data_obj = modem.Data()
    data_obj.read_data_file(dfn)
    data_obj.model_epsg = 32611
# ==============================================================================
# First make the mesh
# ==============================================================================
mod_obj = modem.Model(stations_object=data_obj.station_locations)
mod_obj.cell_size_east = 750
mod_obj.cell_size_north = 750
mod_obj.pad_num = 5
mod_obj.pad_east = 5
mod_obj.pad_north = 5
mod_obj.pad_method = "extent1"
mod_obj.z_mesh_method = "new"
mod_obj.pad_stretch_h = 1.5
mod_obj.pad_stretch_v = 1.2
mod_obj.ew_ext = 350000.0
mod_obj.ns_ext = 350000.0
mod_obj.pad_z = 9
mod_obj.n_layers = 60
mod_obj.n_air_layers = 1
mod_obj.z1_layer = 20
mod_obj.z_target_depth = 80000.0
mod_obj.z_bottom = 300000.0
mod_obj.res_initial_value = 100.0

# --> here is where you can rotate the mesh
mod_obj.mesh_rotation_angle = 0.0

mod_obj.make_mesh()

mod_obj.plot_mesh()
mod_obj.save_path = save_path
mod_obj.write_model_file(
    model_fn_basename="{0}_sm{1:02.0f}_centered.rho".format(
        fn_stem, np.log10(mod_obj.res_initial_value)
    )
)

### =============================================================================
### Add topography
### =============================================================================
if topography:
    mod_obj.data_obj = data_obj
    mod_obj.add_topography_to_model2(topo_fn, airlayer_type="log_down", max_elev=1150)
    mod_obj.write_model_file(
        model_fn_basename=r"{0}_modem_sm02_topo.rho".format(fn_stem)
    )
    mod_obj.plot_topography()

    # change data file to have relative topography
    data_obj.center_stations(mod_obj.model_fn)
    sx, sy = data_obj.project_stations_on_topography(mod_obj)

    mod_obj.plot_mesh(fig_num=2)

##==============================================================================
## make the covariance file
##==============================================================================
cov = modem.Covariance(grid_dimensions=mod_obj.res_model.shape)
cov.smoothing_east = 0.4
cov.smoothing_north = 0.4
cov.smoothing_z = 0.4
cov.smoothing_num = 1

cov.write_covariance_file(
    cov_fn=os.path.join(save_path, "covariance.cov"), model_fn=mod_obj.model_fn
)

mod_obj.write_vtk_file(
    vtk_save_path=save_path, vtk_fn_basename="{0}_sm".format(fn_stem)
)

data_obj.data_array["elev"] = data_obj.data_array["rel_elev"]
data_obj.write_vtk_station_file(
    vtk_save_path=save_path, vtk_fn_basename="{0}_stations".format(fn_stem)
)

mod_obj.print_mesh_params()
