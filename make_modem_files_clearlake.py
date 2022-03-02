# -*- coding: utf-8 -*-
"""
Created on Wed May 25 17:17:14 2016

@author: jpeacock
"""


import os
from pathlib import Path
import numpy as np
import mtpy.modeling.modem as modem

# ==============================================================================
# Inputs
# ==============================================================================
edi_path = Path(r"c:\Users\jpeacock\OneDrive - DOI\ClearLake\modem_inv\inversion_edis")
save_path = Path(r"c:\Users\jpeacock\OneDrive - DOI\ClearLake\modem_inv\inv_02_topo")
topo_fn = Path(r"c:\Users\jpeacock\OneDrive - DOI\ArcGIS\westcoast_etopo.asc")
fn_stem = "cl"

model_epsg = 32610
model_utm_zone = "10S"

# directives on what to do
write_data = False
write_model = True
write_cov = True
write_cfg = False
topography = True
center_stations = True
new_edis = False

s_edi_list = list(edi_path.glob("*.edi"))

remove_list = ["cl126", "cl200"]

for remove in remove_list:
    try:
        s_edi_list.remove(edi_path.joinpath(f"{remove}.edi"))
    except:
        print(f"Could not find {remove} in fn_list")

dfn = Path(r"c:\Users\jpeacock\OneDrive - DOI\ClearLake\modem_inv\inv_01_topo\cl_modem_data_z03_t02_topo_edit_02.dat")
if write_data and dfn.exists():
    os.remove(dfn)

if not os.path.exists(save_path):
    os.mkdir(save_path)

# ==============================================================================
# Make the data file
# ==============================================================================
if not dfn.exists():
    inv_period_list = np.logspace(-np.log10(300), np.log10(2048), num=23)
    data_obj = modem.Data(edi_list=s_edi_list, period_list=inv_period_list)

    data_obj.error_type_z = "eigen_floor"
    data_obj.error_value_z = 3.0
    data_obj.error_type_tipper = "abs_floor"
    data_obj.error_value_tipper = 0.02
    data_obj.inv_mode = "1"
    data_obj.model_epsg = 32710

    # --> here is where you can rotate the data
    data_obj.write_data_file(
        save_path=save_path,
        fn_basename="{0}_modem_data_z{1:02.0f}_t{2:02.0f}.dat".format(
            fn_stem, data_obj.error_value_z, 100 * data_obj.error_value_tipper
        ),
    )

else:
    data_obj = modem.Data()
    data_obj.read_data_file(dfn)
    data_obj.model_epsg = model_epsg
# ==============================================================================
# First make the mesh
# ==============================================================================
if write_model:
    mod_obj = modem.Model(data_obj.station_locations)
    mod_obj.cell_size_east = 500
    mod_obj.cell_size_north = 500
    mod_obj.pad_east = 7
    mod_obj.pad_north = 7
    mod_obj.pad_num = 4
    mod_obj.ew_ext = 300000
    mod_obj.ns_ext = 300000
    mod_obj.z_mesh_method = "new"
    mod_obj.z_bottom = 300000
    mod_obj.z_target_depth = 70000
    mod_obj.pad_z = 5
    mod_obj.n_air_layers = 15
    mod_obj.n_layers = 54
    mod_obj.z1_layer = 30
    mod_obj.pad_stretch_v = 1.8

    # --> here is where you can rotate the mesh
    mod_obj.mesh_rotation_angle = 0

    mod_obj.make_mesh()
    # mod_obj.plot_mesh()

    # mod_obj.write_model_file(save_path=save_path,
    #                         model_fn_basename="{0}_sm02.rho".format(fn_stem))

## =============================================================================
## Add topography
## =============================================================================
if topography:
    mod_obj.add_topography_to_model2(topo_fn, airlayer_type="log_down")
    mod_obj.write_model_file(
        save_path=save_path, model_fn_basename="{0}_sm02_topo.rho".format(fn_stem)
    )
    if center_stations:
        data_obj.center_stations(mod_obj)
    data_obj.project_stations_on_topography(mod_obj)

    mod_obj.plot_mesh(fig_num=3)
    mod_obj.plot_topography()
# ==============================================================================
# make the covariance file
# ==============================================================================
if write_cov:
    cov = modem.Covariance(grid_dimensions=mod_obj.res_model.shape)
    cov.smoothing_east = 0.4
    cov.smoothing_north = 0.4
    cov.smoothing_z = 0.4
    cov.smoothing_num = 1

    cov.write_covariance_file(
        os.path.join(save_path, "covariance.cov"), model_fn=mod_obj.model_fn
    )

    mod_obj.write_vtk_file(
        vtk_save_path=save_path, vtk_fn_basename="{0}_sm_topo".format(fn_stem)
    )
    data_obj.write_vtk_station_file(
        vtk_save_path=save_path, vtk_fn_basename="{0}_stations".format(fn_stem)
    )

    mod_obj.print_mesh_params()
    mod_obj.print_model_file_summary()

# cfg_obj = modem.ModEMConfig()
# cfg_obj.add_dict(obj=data_obj)
# cfg_obj.add_dict(obj=mod_obj)
# cfg_obj.add_dict(obj=cov)
# cfg_obj.write_config_file(save_dir=save_path,
#                          config_fn_basename='Inv01.cfg')
