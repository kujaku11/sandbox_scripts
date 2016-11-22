# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 09:42:44 2015

@author: jpeacock-pr
"""

import numpy as np
import matplotlib.pyplot as plt
import mtpy.modeling.modem_new as modem
import mtpy.utils.latlongutmconversion as ll2utm
import scipy.interpolate as spi
import os

#ascii_fn = r"c:\Users\jpeacock-pr\Documents\MonoBasin\Maps\MonoDEM\ASTER\astgtm2_n37w119_dem.asc"
#ascii_fn = r"c:\Users\jpeacock-pr\Documents\MonoBasin\Maps\MonoDEM\ASTER\astgtm2_n38w119_dem.asc"
dem_fn = r"c:\Users\jpeacock-pr\Documents\LV\Maps\dem_modem.asc"

data_fn = r"c:\MinGW32-xy\Peacock\ModEM\LV\sm_avg_inv3_err12_cov5\lv_dp_23p_err12_tip2.dat"
model_fn = r"c:\MinGW32-xy\Peacock\ModEM\LV\sm_avg_inv3_err12_cov5\lv_err12_cov5_NLCG_019.rho"
modem_center = (337530., 4183900.)
pad = 3
cell_size = 250.
res_air = 1e12
elev_cell = 30

# read in data and model files
m_obj = modem.Model()
m_obj.read_model_file(model_fn)

#--> read in ascii dem file
def read_dem_ascii(ascii_fn, cell_size=500, model_center=(0, 0), rot_90=0):
    """
    read in dem which is ascii format
    
    """
    dfid = file(ascii_fn, 'r')
    d_dict = {}
    for ii in range(6):
        dline = dfid.readline()
        dline = dline.strip().split()
        key = dline[0].strip().lower()
        value = float(dline[1].strip())
        d_dict[key] = value
        
    x0 = d_dict['xllcorner']
    y0 = d_dict['yllcorner']
    nx = int(d_dict['ncols'])
    ny = int(d_dict['nrows'])
    cs = d_dict['cellsize']
    
    # read in the elevation data
    elevation = np.zeros((nx, ny))
    
    for ii in range(1, int(ny)+2):
        dline = dfid.readline()
        if len(str(dline)) > 1:
            #needs to be backwards because first line is the furthest north row.
            elevation[:, -ii] = np.array(dline.strip().split(' '), dtype='float')
        else:
            break
    # need to rotate cause I think I wrote the dem backwards
    elevation = np.rot90(elevation, rot_90)
    dfid.close()

    # create lat and lon arrays from the dem fle
    lon = np.arange(x0, x0+cs*(nx), cs)
    lat = np.arange(y0, y0+cs*(ny), cs)
    
    # calculate the lower left and uper right corners of the grid in meters
    ll_en = ll2utm.LLtoUTM(23, lat[0], lon[0])
    ur_en = ll2utm.LLtoUTM(23, lat[-1], lon[-1])
    
    # estimate cell sizes for each dem measurement
    d_east = abs(ll_en[1]-ur_en[1])/nx
    d_north = abs(ll_en[2]-ur_en[2])/ny

    # calculate the number of new cells
    num_cells = int(cell_size/np.mean([d_east, d_north]))

    # make easting and northing arrays in meters corresponding to lat and lon
    east = np.arange(ll_en[1], ur_en[1], d_east)
    north = np.arange(ll_en[2], ur_en[2], d_north)
    
    #resample the data accordingly
    new_east = east[np.arange(0, east.shape[0], num_cells)]
    new_north = north[np.arange(0, north.shape[0], num_cells)]
    new_x, new_y = np.meshgrid(np.arange(0, east.shape[0], num_cells),
                               np.arange(0, north.shape[0], num_cells),
                               indexing='ij') 
    elevation = elevation[new_x, new_y]
    
    # estimate the shift of the DEM to relative model coordinates
    shift_east = new_east.mean()-model_center[0]
    shift_north = new_north.mean()-model_center[1]
    
    # shift the easting and northing arrays accordingly so the DEM and model
    # are collocated.
    new_east = (new_east-new_east.mean())+shift_east
    new_north = (new_north-new_north.mean())+shift_north
    
    return new_east, new_north, elevation

def interpolate_elevation(elev_east, elev_north, elevation, model_east, 
                          model_north, pad=3):
    """ 
    interpolate the elevation onto the model grid.
    
    Arguments:
    ---------------
    
        *elev_east* : np.ndarray(num_east_nodes)
                      easting grid for elevation model
                      
        *elev_north* : np.ndarray(num_north_nodes)
                      northing grid for elevation model 
                      
        *elevation* : np.ndarray(num_east_nodes, num_north_nodes)
                     elevation model assumes x is east, y is north
                     Units are meters
                     
        *model_east* : np.ndarray(num_east_nodes_model)
                     relative easting grid of resistivity model 
                     
        *model_north* : np.ndarray(num_north_nodes_model)
                     relative northin grid of resistivity model 
                     
        *pad* : int
                number of cells to repeat elevation model by.  So for pad=3,
                then the interpolated elevation model onto the resistivity
                model grid will have the outer 3 cells will be repeats of
                the adjacent cell.  This is to extend the elevation model
                to the resistivity model cause most elevation models will
                not cover the entire area.
                
    Returns:
    --------------
    
        *interp_elev* : np.ndarray(num_north_nodes_model, num_east_nodes_model)
                        the elevation model interpolated onto the resistivity 
                        model grid.
                     
    """
    # need to line up the elevation with the model
    grid_east, grid_north = np.broadcast_arrays(elev_east[:, None],
                                                elev_north[None, :])
    # interpolate onto the model grid
    interp_elev = spi.griddata((grid_east.ravel(), grid_north.ravel()),
                               elevation.ravel(),
                               (model_east[:, None], 
                                model_north[None, :]),
                                method='linear')
                                
    interp_elev[0:pad, pad:-pad] = interp_elev[pad, pad:-pad]
    interp_elev[-pad:, pad:-pad] = interp_elev[-pad-1, pad:-pad]
    interp_elev[:, 0:pad] = interp_elev[:, pad].repeat(pad).reshape(
                                                interp_elev[:, 0:pad].shape)
    interp_elev[:, -pad:] = interp_elev[:, -pad-1].repeat(pad).reshape(
                                                interp_elev[:, -pad:].shape)

    # transpose the modeled elevation to align with x=N, y=E
    interp_elev = interp_elev.T
                          
    return interp_elev   

def make_elevation_model(interp_elev, model_nodes_z, elevation_cell=30, 
                         pad=3, res_air=1e12, fill_res=100):
    """
    Take the elevation data of the interpolated elevation model and map that
    onto the resistivity model by adding elevation cells to the existing model.
    
    ..Note: that if there are large elevation gains, the elevation cell size
            might need to be increased.
            
    Arguments:
    -------------
        *interp_elev* : np.ndarray(num_nodes_north, num_nodes_east)
                        elevation model that has been interpolated onto the
                        resistivity model grid. Units are in meters.
                        
        *model_nodes_z* : np.ndarray(num_z_nodes_of_model)
                          vertical nodes of the resistivity model without
                          topography.  Note these are the nodes given in 
                          relative thickness, not the grid, which is total
                          depth.  Units are meters.
                    
        *elevation_cell* : float
                           height of elevation cells to be added on.  These
                           are assumed to be the same at all elevations. 
                           Units are in meters
                           
        *pad* : int
                number of cells to look for maximum and minimum elevation.
                So if you only want elevations within the survey area, 
                set pad equal to the number of padding cells of the 
                resistivity model grid.
                
        *res_air* : float
                    resistivity of air.  Default is 1E12 Ohm-m
        
        *fill_res* : float
                     resistivity value of subsurface in Ohm-m.
                
    Returns:
    -------------
        *elevation_model* : np.ndarray(num_north_nodes, num_east_nodes, 
                                       num_elev_nodes+num_z_nodes)
                         Model grid with elevation mapped onto it. 
                         Where anything above the surface will be given the
                         value of res_air, everything else will be fill_res
                         
        *new_nodes_z* : np.ndarray(num_z_nodes+num_elev_nodes)
                        a new array of vertical nodes, where any nodes smaller
                        than elevation_cell will be set to elevation_cell.
                        This can be input into a modem.Model object to
                        rewrite the model file.
                                             
    """

    # calculate the max elevation within survey area
    elev_max = interp_elev[pad:-pad, pad:-pad].max()
    elev_min = interp_elev[pad:-pad, pad:-pad].min()
    
    # scale the interpolated elevations to fit within elev_max, elev_min
    interp_elev[np.where(interp_elev > elev_max)] = elev_max
    interp_elev[np.where(interp_elev < elev_min)] = elev_min
    
    # calculate the number of elevation cells needed
    num_elev_cells = int((elev_max-elev_min)/elev_cell)
    print 'Number of elevation cells: {0}'.format(num_elev_cells)
    
    # make an array of just the elevation for the model
    # north is first index, east is second, vertical is third
    elevation_model = np.ones((interp_elev.shape[0],
                               interp_elev.shape[1],
                               num_elev_cells+model_nodes_z.shape[0]))
                               
    elevation_model[:, :, :] = fill_res
         
    # fill in elevation model with air values.  Remeber Z is positive down, so
    # the top of the model is the highest point                
    for nn in range(interp_elev.shape[0]):
        for ee in range(interp_elev.shape[1]):
            dz = int((elev_max-interp_elev[nn, ee])/elev_cell)
            elevation_model[nn, ee, 0:dz] = res_air
    
    
    
    new_nodes_z = np.append(np.repeat(elevation_cell, num_elev_cells), 
                            model_nodes_z) 
                            
    new_nodes_z[np.where(new_nodes_z < elevation_cell)] = elevation_cell
    
    return elevation_model, new_nodes_z
    
def change_data_elevation(data_fn, model_fn, new_data_fn=None, res_air=1e12):
    """
    At each station in the data file rewrite the elevation, so the station is
    on the surface, not floating in air.
    
    Arguments:
    ------------------
        *data_fn* : string
                    full path to a ModEM data file
                    
        *model_fn* : string
                    full path to ModEM model file that has elevation 
                    incoorporated.
                                        
        *new_data_fn* : string
                        full path to new data file name.  If None, then 
                        new file name will add _elev.dat to input filename
                        
        *res_air* : float
                    resistivity of air.  Default is 1E12 Ohm-m
    Returns:
    -------------
        *new_data_fn* : string
                        full path to new data file.
    """
    
    d_obj = modem.Data()
    d_obj.read_data_file(data_fn)
    
    m_obj = modem.Model()
    m_obj.read_model_file(model_fn)
    
    for key in d_obj.mt_dict.keys():
        mt_obj = d_obj.mt_dict[key]
        e_index = np.where(m_obj.grid_east > mt_obj.grid_east)[0][0]
        n_index = np.where(m_obj.grid_north > mt_obj.grid_north)[0][0]
        z_index = np.where(m_obj.res_model[n_index, e_index, :] < res_air*.9)[0][0]
        s_index = np.where(d_obj.data_array['station']==key)[0][0]        
        d_obj.data_array[s_index]['elev'] = m_obj.grid_z[z_index]
        
        print '-'*30
        print e_index, mt_obj.grid_east, m_obj.grid_east[e_index]
        print n_index, mt_obj.grid_north, m_obj.grid_north[n_index]
        print z_index, m_obj.grid_z[z_index]
                
        mt_obj.grid_elev = m_obj.grid_z[z_index]
        print key, d_obj.data_array[s_index]['elev'], mt_obj.grid_elev 
        
    if new_data_fn is None:
        new_dfn = '{0}{1}'.format(data_fn[:-4], '_elev.dat')
    else:
        new_dfn=new_data_fn
        
    d_obj.write_data_file(save_path=os.path.dirname(new_dfn), 
                          fn_basename=os.path.basename(new_dfn),
                          compute_error=False)
         
    return new_dfn

def write_covariance_file(model_fn, cov_east=0.3, cov_north=0.3, cov_z=0.3,
                          sea_water=0.3):
    """
    write a covariance file that converts air and sea into numbers 
    for the covariance matrix
    """
    
    model_obj = modem.Model()
    model_obj.read_model_file(model_fn)    

    model_res = model_obj.res_model.copy()
    
    mask_arr = np.ones_like(model_res)
    mask_arr[np.where(model_res > 1e10)] = 0
    mask_arr[np.where((model_res < sea_water*1.1) & 
                      (model_res > sea_water*.9))] = 9
    
    cov = modem.Covariance()
    cov.grid_dimensions = model_res.shape
    
    cov.smoothing_east = cov_east
    cov.smoothing_north = cov_north
    cov.smoothing_z = cov_z
    cov.mask_arr = mask_arr.copy()    
    
    cov.write_covariance_file(save_path=model_obj.save_path)
    
    return cov.mask_arr, mask_arr
    
                    
#==============================================================================
#  Do all the work
#==============================================================================
#### 1.) read in the dem and center it onto the resistivity model 
#e_east, e_north, elevation = read_dem_ascii(dem_fn, cell_size=500, 
#                                        model_center=modem_center, 
#                                        rot_90=3)
#
#### 2.) interpolate the elevation model onto the model grid
#m_elev = interpolate_elevation(e_east, e_north, elevation, 
#                               m_obj.grid_east, m_obj.grid_north, pad=3)
#
#### 3.) make a resistivity model that incoorporates topography
#mod_elev, elev_nodes_z = make_elevation_model(m_elev, m_obj.nodes_z, 
#                                              elevation_cell=elev_cell) 
#
#### 4.) write new model file  
#m_obj.nodes_z = elev_nodes_z
#m_obj.res_model = mod_elev
#m_obj.write_model_file(save_path=r"c:\MinGW32-xy\Peacock\ModEM\LV\Topography_test",
#                       model_fn_basename='sm_topography.rho')
#
# write new data file                       
#n_dfn = change_data_elevation(data_fn, m_obj.model_fn, 
#                              new_data_fn=r"c:\MinGW32-xy\Peacock\ModEM\LV\Topography_test\ModEM_data_elev.dat")

#mfn = r"c:\MinGW32-xy\Peacock\ModEM\LV\Topography_test\sm_topography_ml.rho"
## write covariance file
#m_arr_cov, m_arr = write_covariance_file(mfn, 
#                                         cov_east=0.4, 
#                                         cov_north=0.4, 
#                                         cov_z=0.4,
#                                         sea_water=.15)

#fig = plt.figure(1)
#fig.clf()
#
#d_obj = modem.Data()
#d_obj.read_data_file(data_fn)
#
#ax1 = fig.add_subplot(1,2,1, aspect='equal')
##im = ax.imshow(np.rot90(elevation), cmap='gist_earth', origin='lower',
##          extent=(min(new_east), max(new_east),
##                  min(new_north), max(new_north)),
##          vmin=1600, vmax=4000)
#
#
#mod_x, mod_y = np.meshgrid(m_obj.grid_east, m_obj.grid_north)
#
##im2 = ax.pcolormesh(mod_x, mod_y, np.log10(m_obj.res_model[:, :, 29]),
##                    cmap='seismic_r',
##                   vmin=-1, vmax=4)
#                   
#im = ax1.pcolormesh(mod_x, mod_y, m_elev, cmap='gist_earth',
#                   vmin=1000, vmax=3500)
#  
#ax2 = fig.add_subplot(1, 2, 2, aspect='equal')
#im2 = ax2.pcolormesh(elev_east, elev_north, elevation, cmap='gist_earth',
#                   vmin=1000, vmax=3500)
#
#for ax in [ax1, ax2]:
#    ax.scatter(d_obj.station_locations['rel_east'], 
#               d_obj.station_locations['rel_north'],
#               marker='v')
#    ax.set_xlabel('Easting (m)')
#    ax.set_ylabel('Northing (m)')
#plt.colorbar(im)
#
#plt.show()                 
                 
# need to calculate mininum and maximum to get an idea of what the elevation 
# difference is.  The the max will be the top of the model and fill in down
# to minimum value. 


