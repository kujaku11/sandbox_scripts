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
import json
import mtpy.modeling.modem as modem
import mtpy.core.mt as mt

# =============================================================================
# Parameters
# =============================================================================
edi_path = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GreatBasin\modem_inv\inv_02\edi_files"
)
save_path = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GreatBasin\modem_inv\inv_03"
)
topo_fn = r"c:\Users\jpeacock\OneDrive - DOI\MusicValley\mv_topo.asc"
averaged_stations = r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GreatBasin\modem_inv\inv_02\averaged_station_names.json"

fn_stem = "gb"

overwrite = False
topography = False


bounds = {"lat": np.array([37.25, 41.5]), "lon": np.array([-124.5, -114.5])}

dfn = save_path.joinpath("{0}_modem_data_z03_t02.dat".format(fn_stem))
if overwrite and dfn.exists():
    os.remove(dfn)

if not save_path.exists():
    save_path.mkdir()
# =============================================================================
# Get edi files
# =============================================================================
if not dfn.exists():
    s_edi_list = list(edi_path.glob("*.edi"))
#     edi_list = [fn for fn in list(edi_path.glob('*.edi'))]
#     s_edi_list = []
#     mt_list = []
#     for edi in edi_list:
#         mt_obj = mt.MT(edi)
#         if mt_obj.lat >= bounds['lat'].min() and mt_obj.lat <= bounds['lat'].max():
#             if mt_obj.lon >= bounds['lon'].min() and mt_obj.lon <= bounds['lon'].max():
#                 s_edi_list.append(edi)
#                 mt_list.append(mt_obj)


# ==============================================================================
# Make the data file
# ==============================================================================
if not dfn.exists():
    inv_period_list = np.logspace(np.log10(1.0 / 100), np.log10(30000), num=23)
    data_obj = modem.Data(edi_list=s_edi_list, period_list=inv_period_list)
    data_obj.error_type_z = "eigen_floor"
    data_obj.error_value_z = 3.0
    data_obj.error_type_tipper = "abs_floor"
    data_obj.error_value_tipper = 0.02
    data_obj.inv_mode = "1"
    data_obj.model_epsg = 32611
    data_obj.get_mt_dict()
    data_obj.fill_data_array()

    # --> here is where you can rotate the data
    data_obj.rotation_angle = 0

    # # check for multiple stations in single cell
    # r = 12000
    # count = 1
    # s_list = []
    # for ee in np.arange(data_obj.data_array['rel_east'].min(),
    #                     data_obj.data_array['rel_east'].max(),
    #                     r):
    #     for nn in np.arange(data_obj.data_array['rel_north'].min(),
    #                     data_obj.data_array['rel_north'].max(),
    #                     r):
    #         avg_z = data_obj.data_array[np.where((data_obj.data_array['rel_east'] >= ee) &
    #                                              (data_obj.data_array['rel_east'] <= ee + r) &
    #                                              (data_obj.data_array['rel_north'] > nn) &
    #                                              (data_obj.data_array['rel_north'] <= nn +r))]
    #         if len(avg_z['lat']) > 1:
    #             mt_avg = mt.MT()
    #             avg_z['z'][np.where(avg_z['z'] == 0+0j)] = np.nan+1j*np.nan
    #             avg_z['z_err'][np.where(avg_z['z_err'] == 0)] = np.nan
    #             avg_z['tip'][np.where(avg_z['z'] == 0+0j)] = np.nan+1j*np.nan
    #             avg_z['tip_err'][np.where(avg_z['z_err'] == 0)] = np.nan

    #             mt_avg.Z = mt.MTz.Z(z_array=np.nanmean(avg_z['z'], axis=0),
    #                                 z_err_array=np.nanmean(avg_z['z_err'], axis=0),
    #                                 freq=1./data_obj.period_list)
    #             mt_avg.Tipper = mt.MTz.Tipper(tipper_array=np.nanmean(avg_z['tip'], axis=0),
    #                                 tipper_err_array=np.nanmean(avg_z['tip_err'], axis=0),
    #                                 freq=1./data_obj.period_list)
    #             mt_avg.lat = avg_z['lat'].mean()
    #             mt_avg.lon = avg_z['lon'].mean()
    #             mt_avg.elev = avg_z['elev'].mean()
    #             mt_avg.station = f'AVG{count:03}'
    #             mt_avg.Notes.info_dict["avgeragd_stations"] = ', '.join(avg_z['station'].tolist())
    #             mt_avg.write_mt_file(save_dir=save_path)

    #             s_list.append({'count': count, 'stations': avg_z['station'].tolist()})
    #             count += 1

    #         else:
    #             continue

    data_obj.write_data_file(
        save_path=save_path,
        fn_basename="{0}_modem_data_z{1:02.0f}_t{2:02.0f}.dat".format(
            fn_stem, data_obj.error_value_z, 100 * data_obj.error_value_tipper
        ),
        fill=False,
    )
else:
    data_obj = modem.Data()
    data_obj.read_data_file(dfn)
    data_obj.model_epsg = 32611
# ==============================================================================
# First make the mesh
# ==============================================================================
mod_obj = modem.Model(stations_object=data_obj.station_locations)
mod_obj.cell_size_east = 8000
mod_obj.cell_size_north = 8000.0
mod_obj.pad_num = 2
mod_obj.pad_east = 12
mod_obj.pad_north = 12
mod_obj.pad_method = "extent1"
mod_obj.z_mesh_method = "new"
mod_obj.pad_stretch_h = 1.11
mod_obj.pad_stretch_v = 1.25
mod_obj.ew_ext = 350000.0
mod_obj.ns_ext = 350000.0
mod_obj.pad_z = 9
mod_obj.n_layers = 60
mod_obj.n_air_layers = 1
mod_obj.z1_layer = 100
mod_obj.z_target_depth = 100000.0
mod_obj.z_bottom = 300000.0
mod_obj.res_initial_value = 100.0

# --> here is where you can rotate the mesh
mod_obj.mesh_rotation_angle = 0.0

mod_obj.make_mesh()

# new_north = list(mod_obj.nodes_north[0:4]) + \
#             [round(2000 + 2000*.15*ii) for ii in range(12)][::-1] +\
#             [1500] * 75 +\
#             [round(2000 + 2000*.15*ii) for ii in range(5)] +\
#             list(mod_obj.nodes_north[0:4])[::-1]

# new_east = list(mod_obj.nodes_east[0:3]) + \
#             [round(2000 + 2000*.15*ii) for ii in range(15)][::-1] +\
#             [1500] * 80 +\
#             [round(2000 + 2000*.15*ii) for ii in range(5)] +\
#             list(mod_obj.nodes_east[0:4])[::-1]
# mod_obj.nodes_north = new_north
# mod_obj.grid_north -= mod_obj.grid_north.mean()

# mod_obj.nodes_east = new_east
# mod_obj.grid_east -= mod_obj.grid_east.mean()

# mod_obj.res_model = np.ones((mod_obj.nodes_north.size,
#                               mod_obj.nodes_east.size,
#                               mod_obj.nodes_z.size))
mod_obj.res_model[:] = mod_obj.res_initial_value

mod_obj.plot_mesh()
mod_obj.save_path = save_path
mod_obj.write_model_file(
    model_fn_basename="{0}_sm{1:02.0f}.rho".format(
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
