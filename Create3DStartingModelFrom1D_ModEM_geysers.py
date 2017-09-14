# -*- coding: utf-8 -*-
"""
Created on Thu Oct 31 14:00:21 2013

@author: jpeacock-pr
"""
#==============================================================================
# Imports
#==============================================================================
import os
import numpy as np
import scipy.interpolate as interpolate
import scipy.signal as signal
import scipy.ndimage as ndimage

import mtpy.modeling.modem as modem
import mtpy.modeling.occam1d as occam1d
#==============================================================================
# Inputs
#==============================================================================
model_fn = r"c:\Users\jpeacock\Documents\ClearLake\modem_inv\inv03\gz_err03_cov02_NLCG_127.rho"
data_fn = r"C:\Users\jpeacock\Documents\ClearLake\modem_inv\inv03\gz_data_err03_tec.dat"
npy_fn = os.path.join(os.path.dirname(model_fn), 'np_res_array_1d.npy')

save_dir = os.path.dirname(data_fn)
opath = 'c:\\MinGW32-xy\\Peacock\\occam\\occam1d.exe'
iter_num = 4
fill_res = np.log10(50.)
plot = False

#==============================================================================
# Read data and model files
#==============================================================================
mdd = modem.Data()
mdd.read_data_file(data_fn)

mdm = modem.Model()
mdm.read_model_file(model_fn)


#==============================================================================
# check to see if there is a npy file first, if there isn't make one
# this way we won't have to redo the 1D inversions
#==============================================================================
if not os.path.exists(npy_fn):
    oned_res_arr = np.zeros(len(mdd.mt_dict.keys()), dtype=[('station', 'S10'),
                                                            ('grid_east', np.float),
                                                            ('grid_north', np.float),
                                                            ('grid_elev', np.float),
                                                            ('res', (np.float, mdm.grid_z.shape))])
    
    #--> compute 1D models 
    for dd, key in enumerate(sorted(mdd.mt_dict.keys())):
        mt_obj = mdd.mt_dict[key]
        occam_sv_path = os.path.join(save_dir, mt_obj.station)
        iter_fn = os.path.join(occam_sv_path, 'Det_{0}.iter'.format(iter_num))
        resp_fn = os.path.join(occam_sv_path, 'Det_{0}.resp'.format(iter_num))
        m_fn = os.path.join(occam_sv_path, 'Model1D')
        
        # check to see if inversions already exist
        if os.path.exists(iter_fn):
                                    
            ocm = occam1d.Model()
            ocm.read_iter_file(iter_fn, m_fn)
            oned_res_arr[dd]['station'] = mt_obj.station
            oned_res_arr[dd]['grid_east'] = mt_obj.grid_east
            oned_res_arr[dd]['grid_north'] = mt_obj.grid_north
            oned_res_arr[dd]['grid_elev'] = mt_obj.grid_elev
            
            # need to find elevation
            depth_index = np.where(mdm.grid_z == mt_obj.grid_elev)[0][0]
            depth_res = np.repeat(fill_res, depth_index)
            depth_res = np.append(depth_res, ocm.model_res[2:, 1])
            oned_res_arr[dd]['res'] = depth_res[0:mdm.res_model.shape[2]+1]
            
            if plot:
                pr = occam1d.Plot1DResponse(data_te_fn=os.path.join(occam_sv_path,
                                                                    'Occam1d_DataFile_DET.dat'),
                                            model_fn=os.path.join(occam_sv_path,
                                                                    'Model1D'),
                                            resp_te_fn=resp_fn,
                                            iter_te_fn=iter_fn, 
                                            depth_limits=(0, 20))
                pr.save_figure(os.path.join(save_dir,
                                            '{0}_1d_resp.png'.format(mt_obj.station)),
                               fig_dpi=900)
        else:
            mt_obj.Z.compute_resistivity_phase()
            rho = mt_obj.Z.resistivity
            rho_err = mt_obj.Z.resistivity_err
            phi = mt_obj.Z.phase
            phi_err = mt_obj.Z.phase_err
            rp_tup = (mt_obj.Z.freq, rho, rho_err, phi, phi_err)
        
            #--> write occam1d data file             
            ocd = occam1d.Data()
            ocd.save_path = os.path.join(save_dir, mt_obj.station)
            ocd.write_data_file(rp_tuple=rp_tup,
                                mode='det', 
                                res_err=10, 
                                phase_err=2.5)
            data_tm_fn = ocd.data_fn    
            
            #--> write occam1d model file
            ocm = occam1d.Model()
            ocm.save_path = ocd.save_path
            ocm.write_model_file(model_depth=mdm.grid_z)
            
            #--> write occam1d startup file
            ocs = occam1d.Startup()
            ocs.data_fn = data_tm_fn
            ocs.model_fn = ocm.model_fn
            ocs.save_path = ocd.save_path
            ocs.max_iter = iter_num+1
            ocs.write_startup_file()
            
            #--> run occam1d
            occam1d.Run(ocs.startup_fn, occam_path=opath, mode='Det')
            
            try:
                iter_fn = os.path.join(ocd.save_path, 'Det_{0}.iter'.format(iter_num))
                resp_fn = os.path.join(ocd.save_path, 'Det_{0}.resp'.format(iter_num))
                ocm.read_iter_file(iter_fn)
                oned_res_arr[dd]['station'] = mt_obj.station
                oned_res_arr[dd]['grid_east'] = mt_obj.grid_east
                oned_res_arr[dd]['grid_north'] = mt_obj.grid_north
                oned_res_arr[dd]['grid_elev'] = mt_obj.grid_elev
                
                # need to find elevation
                depth_index = np.where(mdm.grid_z == mt_obj.grid_elev)[0][0]
                depth_res = np.repeat(fill_res, depth_index)
                depth_res = np.append(depth_res, ocm.model_res[2:, 1])
                oned_res_arr[dd]['res'] = depth_res[0:mdm.res_model.shape[2]+1]
                if plot:
                    pr = occam1d.Plot1DResponse(data_te_fn=ocd.data_fn,
                                                model_fn=ocm.model_fn,
                                                resp_te_fn=resp_fn,
                                                iter_te_fn=iter_fn, 
                                                depth_limits=(0, 20))
                    pr.save_figure(os.path.join(save_dir,
                                                '{0}_1d_resp.png'.format(mt_obj.station)),
                                   fig_dpi=900)
                        
        
            except IOError:
                print '-'*50
                print '\t{0} did not run properly, check occam1d files'.format(mt_obj.station)
                print '-'*50
        
    # trim array if some station was acting up
    nz = np.nonzero(oned_res_arr['grid_east'])
    oned_res_arr = oned_res_arr[nz]
    
    # save file so we don't have to do this over again
    np.save(os.path.join(os.path.dirname(model_fn), 'np_res_array_1d.npy'),
            oned_res_arr)
# otherwise load the npy file
else:
    oned_res_arr = np.load(npy_fn)
    
#==============================================================================
# # now interpolate onto grid
#==============================================================================
data_points = np.array([oned_res_arr['grid_north'], oned_res_arr['grid_east']])

pad_n = mdm.pad_north
pad_e = mdm.pad_east

x = mdm.grid_north[pad_n:-pad_n-1]
y = mdm.grid_east[pad_e:-pad_e-1]

new_north, new_east = np.meshgrid(x, y)

# apply a median filter to get rid of outlying points
rs = signal.medfilt2d(oned_res_arr['res'], kernel_size=(5, 3))

new_res = np.zeros_like(mdm.res_model)
for z_index in range(mdm.nodes_z.size):
    new_res[pad_n:-pad_n, pad_e:-pad_e,  z_index] = interpolate.griddata(data_points.T,
                                                  rs[:, z_index],
                                                  (new_north, new_east),
                                                  method='cubic',
                                                  fill_value=fill_res).T
                                                      
new_res[np.where(new_res == 0.0)] = fill_res
#==============================================================================
# # need to fill the model so there are no hard boundaries
#==============================================================================
def decay(a_0, a_1, x):
    nx = x.size
    na = a_0.size
    k = (1./nx)*np.log(a_0/a_1)
    
    #reshape things for faster calculations
    x_arr = x.repeat(na).reshape((nx, na))
    r_arr = a_0.repeat(nx).reshape((na, nx))
    k_arr = k.repeat(nx).reshape((na, nx))
    
    res_decay = r_arr.T*np.exp(-k_arr.T*x_arr)

    return res_decay

for n_index in range(new_res.shape[0]):
    for e_index in range(pad_e, new_res.shape[1]-pad_e, 1):
        try:
            # --> left hand side
            left_index = np.where(new_res[:, e_index, 0] != fill_res)[0][0]
            if left_index == 0:
                continue
            
            res_decay = decay(new_res[left_index, e_index, :], 
                             fill_res,
                             np.arange(left_index))
            
            new_res[0:left_index, e_index, :] = res_decay[::-1, :]
            
            # --> right hand side
            right_index = np.where(new_res[:, e_index, 0] != fill_res)[0][-1]
            
            if right_index == new_res.shape[0]-1:
                continue
            
            res_decay = decay(new_res[right_index, e_index, :], 
                             fill_res,
                             np.arange(new_res.shape[0]-right_index))
            
            new_res[right_index:, e_index, :] = res_decay
            
        except IndexError:
            pass
        
    #--> go east west
    try:
        left_index = np.where(new_res[n_index, :, 0] != fill_res)[0][0]
        if left_index == 0:
            continue
        
        res_decay = decay(new_res[n_index, left_index, :], 
                          fill_res,
                          np.arange(left_index))
        
        new_res[n_index, 0:left_index, :] = res_decay[::-1, :]
        
        #--> do the right hand side
        right_index = np.where(new_res[n_index, :, 0] != fill_res)[0][-1]
        
        if right_index == new_res.shape[1]-1:
            continue
        
        res_decay = decay(new_res[n_index, right_index, :], 
                             fill_res,
                             np.arange(new_res.shape[1]-right_index))
        
        new_res[n_index, right_index:, :] = res_decay
        
    except IndexError:
        pass
#==============================================================================
# finally smooth the result
#==============================================================================
new_res = ndimage.gaussian_filter(new_res, 1.5)
new_res = 10**new_res
new_res[np.where(mdm.res_model > 1E9)] = 1E12


mdm.res_model = new_res
mdm.write_model_file(model_fn_basename=r"geysers_1d_sm.rho")
    

    
    