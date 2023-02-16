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
from mtpy.modeling import modem
from mtpy.core import mt
from mtpy.core import mt_collection

# =============================================================================
# Parameters
# =============================================================================
edi_path = Path(r"c:\Users\jpeacock\OneDrive - DOI\EDI_FILES")
csv_fn = r"c:\Users\jpeacock\OneDrive - DOI\EDI_FILES\all_mt_stations.csv"
save_path = Path(r"c:\Users\jpeacock\OneDrive - DOI\LV\Inversions\inv_all_01")
topo_fn = r"c:\Users\jpeacock\OneDrive - DOI\ArcGIS\westcoast_etopo.asc"

fn_stem = "lvmb"

bounds = {"lat": np.array([37.25, 38.35]), "lon": np.array([-119.25, -118.5])}
# bounds = None

avg_radius = 6000
model_epsg = 26911

# directives on what to do
write_data = False
write_model = True
write_cov = True
write_cfg = False
topography = True
center_stations = True
new_edis = False

dfn = save_path.joinpath("{0}_modem_data_z03_t02_topo_02.dat".format(fn_stem))
if write_data and dfn.exists():
    os.remove(dfn)

if not save_path.exists():
    save_path.mkdir()

# ==============================================================================
# Make the data file
# ==============================================================================
if not dfn.exists():

    # =============================================================================
    # Get edi files
    # =============================================================================
    if not dfn.exists():
        if bounds is not None:
            mc = mt_collection.MTCollection()
            mc.from_csv(csv_fn)
            new_mc = mc.apply_bbox(
                bounds["lon"].min(),
                bounds["lon"].max(),
                bounds["lat"].min(),
                bounds["lat"].max(),
            )

            s_edi_list = new_mc.dataframe.fn.to_list()
        else:
            s_edi_list = list(edi_path.glob("*.edi"))

    inv_period_list = np.logspace(np.log10(1.0 / 300), np.log10(2048), num=23)
    data_obj = modem.Data(edi_list=s_edi_list, period_list=inv_period_list)
    data_obj.error_type_z = "eigen_floor"
    data_obj.error_value_z = 3.0
    data_obj.error_type_tipper = "abs_floor"
    data_obj.error_value_tipper = 0.02
    data_obj.inv_mode = "1"
    data_obj.model_epsg = model_epsg
    data_obj.data_array, data_obj.mt_dict = data_obj.fill_data_array(
        data_obj.mt_dict
    )

    # --> here is where you can rotate the data
    data_obj.rotation_angle = 0

    # # check for multiple stations in single cell
    if new_edis:
        new_edi_path = save_path.joinpath("new_edis")
        if not new_edi_path.exists():
            new_edi_path.mkdir()

        print("--- averaging stations ---")
        r = avg_radius
        count = 1
        s_list = []
        for ee in np.arange(
            data_obj.data_array["rel_east"].min(),
            data_obj.data_array["rel_east"].max(),
            r,
        ):
            for nn in np.arange(
                data_obj.data_array["rel_north"].min(),
                data_obj.data_array["rel_north"].max(),
                r,
            ):
                avg_z = data_obj.data_array[
                    np.where(
                        (data_obj.data_array["rel_east"] >= ee)
                        & (data_obj.data_array["rel_east"] <= ee + r)
                        & (data_obj.data_array["rel_north"] > nn)
                        & (data_obj.data_array["rel_north"] <= nn + r)
                    )
                ]
                if len(avg_z["lat"]) > 1:
                    mt_avg = mt.MT()
                    avg_z["z"][np.where(avg_z["z"] == 0 + 0j)] = (
                        np.nan + 1j * np.nan
                    )
                    avg_z["z_err"][np.where(avg_z["z_err"] == 0)] = np.nan
                    avg_z["tip"][np.where(avg_z["z"] == 0 + 0j)] = (
                        np.nan + 1j * np.nan
                    )
                    avg_z["tip_err"][np.where(avg_z["z_err"] == 0)] = np.nan

                    mt_avg.Z = mt.MTz.Z(
                        z_array=np.nanmean(avg_z["z"], axis=0),
                        z_err_array=np.nanmean(avg_z["z_err"], axis=0),
                        freq=1.0 / data_obj.period_list,
                    )
                    mt_avg.Tipper = mt.MTz.Tipper(
                        tipper_array=np.nanmean(avg_z["tip"], axis=0),
                        tipper_err_array=np.nanmean(avg_z["tip_err"], axis=0),
                        freq=1.0 / data_obj.period_list,
                    )
                    mt_avg.latitude = avg_z["lat"].mean()
                    mt_avg.longitude = avg_z["lon"].mean()
                    mt_avg.elevation = avg_z["elev"].mean()
                    mt_avg.station = f"AVG{count:03}"
                    mt_avg.station_metadata.comments = (
                        "avgeraged_stations = "
                        + ",".join(avg_z["station"].tolist())
                    )
                    edi_obj = mt_avg.write_mt_file(save_dir=new_edi_path)
                    print(f"wrote average file {edi_obj.fn}")

                    s_list.append(
                        {"count": count, "stations": avg_z["station"].tolist()}
                    )
                    count += 1

                    # remove averaged stations
                    try:
                        (
                            data_obj.data_array,
                            data_obj.mt_dict,
                        ) = data_obj.remove_station(avg_z["station"].tolist())
                    except KeyError:
                        print("Could not remove {avg_z['station'].tolist()}")

                    # add averaged station
                    (
                        data_obj.data_array,
                        data_obj.mt_dict,
                    ) = data_obj.add_station(mt_object=mt_avg)

                else:
                    continue

    data_obj.write_data_file(
        save_path=save_path,
        fn_basename=f"{fn_stem}_modem_data_z{data_obj.error_value_z:02.0f}_t{100 * data_obj.error_value_tipper:02.0f}.dat",
        fill=False,
        new_edis=new_edis,
    )
else:
    data_obj = modem.Data()
    data_obj.read_data_file(dfn)
    data_obj.model_epsg = model_epsg
# ==============================================================================
# First make the mesh
# ==============================================================================
if write_model:
    mod_obj = modem.Model(stations_object=data_obj.station_locations)
    mod_obj.cell_size_east = 500.0
    mod_obj.cell_size_north = 500.0
    mod_obj.pad_num = 3
    mod_obj.pad_east = 10
    mod_obj.pad_north = 10
    mod_obj.pad_method = "extent1"
    mod_obj.z_mesh_method = "new"
    mod_obj.pad_stretch_h = 1.2
    mod_obj.pad_stretch_v = 1.25
    mod_obj.ew_ext = 200000
    mod_obj.ns_ext = 200000
    mod_obj.pad_z = 9
    mod_obj.n_layers = 65
    mod_obj.n_air_layers = 30
    mod_obj.z1_layer = 35
    mod_obj.z_target_depth = 80000.0
    mod_obj.z_bottom = 300000.0
    mod_obj.res_initial_value = 100.0
    mod_obj.z_layer_rounding = 0

    # --> here is where you can rotate the mesh
    mod_obj.mesh_rotation_angle = 0.0

    mod_obj.make_mesh()

    mod_obj.res_model[:] = mod_obj.res_initial_value

    if not topography:
        mod_obj.plot_mesh()
    mod_obj.save_path = save_path
    mod_obj.write_model_file(
        model_fn_basename="{0}_sm{1:02.0f}.rho".format(
            fn_stem, np.log10(mod_obj.res_initial_value)
        )
    )

# =============================================================================
# Add topography
# =============================================================================
if topography:
    mod_obj.data_obj = data_obj
    mod_obj.station_locations.model_epsg = model_epsg
    mod_obj.add_topography_to_model2(
        topo_fn,
        # airlayer_type="log_down",
        airlayer_type="constant",
        shift_north=0,
        shift_east=0,
        max_elev=3050,
    )
    mod_obj.write_model_file(
        model_fn_basename=r"{0}_modem_sm02_topo.rho".format(fn_stem)
    )

    # change data file to have relative topography
    if center_stations:
        data_obj.station_locations.calculate_rel_locations()
        data_obj.center_stations(mod_obj)
    data_obj.project_stations_on_topography(mod_obj)
    mod_obj.station_locations = data_obj.station_locations

    mod_obj.plot_topography()
    mod_obj.plot_mesh()
    mod_obj.print_mesh_params()

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
        cov_fn=os.path.join(save_path, "covariance.cov"),
        model_fn=mod_obj.model_fn,
    )

    # mod_obj.write_vtk_file(
    #     vtk_save_path=save_path, vtk_fn_basename="{0}_sm".format(fn_stem)
    # )

    # data_obj.data_array["elev"] = data_obj.data_array["rel_elev"]
    # data_obj.write_vtk_station_file(
    #     vtk_save_path=save_path, vtk_fn_basename="{0}_stations".format(fn_stem)
    # )

    # mod_obj.print_mesh_params()
