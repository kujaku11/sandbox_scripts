# -*- coding: utf-8 -*-
"""
Created on Mon May 16 14:23:24 2016

@author: jpeacock
"""

import mtpy.analysis.geometry as MTge
import numpy as np
import mtpy.core.mt as mt
import copy
import mtpy.utils.calculator as MTcc
import mtpy.imaging.mtplot as mtplot
import os

edi_fn = r"c:\Users\jrpeacock\Documents\Test_Data\HalfSpaceSQC\par16ew.edi"
edi_fn_d = '{0}_d.edi'.format(edi_fn[0:-4])
edi_fn_dr = '{0}_dr.edi'.format(edi_fn[0:-4])

if os.path.isfile(edi_fn_d) == True:
    os.remove(edi_fn_d)
    
if os.path.isfile(edi_fn_dr) == True:
    os.remove(edi_fn_dr)
    
mt1 = mt.MT(edi_fn)
nf = 16

D = np.array([[1.00, .02],
              [.02, .90]])
              
mt1.Z.z = np.dot(mt1.Z.z, D)
mt1.write_edi_file(edi_fn_d)


#def find_distortion(z_object, g = 'det', lo_dims = None):
#    """
#    find optimal distortion tensor from z object
#
#    automatically determine the dimensionality over all frequencies, then find
#    the appropriate distortion tensor D
#    """


z_obj = copy.deepcopy(mt1.Z)
z_obj.z = z_obj.z[0:nf]
z_obj.z_err = z_obj.z_err[0:nf]
z_obj.freq = z_obj.freq[0:nf]

z_obj.z[10, :, :] = 0.0+0.0j


g = 'det'

dim_arr = MTge.dimensionality(z_object=z_obj)
st_arr = -1*MTge.strike_angle(z_object=z_obj)[:, 0]

dis = np.zeros_like(z_obj.z, dtype=np.float)
dis_err = np.ones_like(z_obj.z, dtype=np.float)


#dictionary of values that should be no distortion in case distortion
#cannot be calculated for that component

rot_mat = np.matrix([[0, -1], [1, 0]])
for idx, dim in enumerate(dim_arr):
    if np.any(z_obj.z[idx] == 0.0+0.0j) == True:
        dis[idx] = np.identity(2)
        print 'Found a zero at {0}'.format(idx)
        
        continue
    
    if dim == 1:

        print '1D at index {0}'.format(idx)
        if g in ['01', '10']:
            gr = np.abs(z_obj.z.real[idx, int(g[0]), int(g[1])])
            gi = np.abs(z_obj.z.imag[idx, int(g[0]), int(g[1])])
        else:
            gr = np.sqrt(np.linalg.det(z_obj.z.real[idx]))
            gi = np.sqrt(np.linalg.det(z_obj.z.imag[idx]))

        dis[idx] = np.mean(np.array([(1./gr*np.dot(z_obj.z.real[idx], rot_mat)),
                                    (1./gi*np.dot(z_obj.z.imag[idx], rot_mat))]),
                            axis=0)  

        if z_obj.z_err is not None:
            #find errors of entries for calculating weights

            gr_err = 1./gr*np.abs(z_obj.z_err[idx])
            gr_err[np.where(gr_err == 0.0)] = 1.0 
            
            gi_err = 1./gi*np.abs(z_obj.z_err[idx])
            gi_err[np.where(gi_err == 0.0)] = 1.0 
            
            dis_err[idx] = np.mean(np.array([gi_err, gr_err]), 
                                   axis=0)
                                   
    elif dim == 2:
        P = 1
        strike_ang = st_arr[idx]
        if np.isnan(strike_ang):
            strike_ang = 0.0
        
        if z_obj.z_err is not None:
            err_arr = z_obj.z_err[idx]
            err_arr[np.where(err_arr == 0.0)] = 1.0
        else:
            err_arr = None
            
        tetm_arr, tetm_err = MTcc.rotatematrix_incl_errors(z_obj.z[idx], 
                                                           strike_ang, 
                                                           inmatrix_err=err_arr)
        
        tetm_r = tetm_arr.real
        tetm_i = tetm_arr.imag
        t_arr_r = -4*P*tetm_r[0, 1]*tetm_r[1, 0]/np.linalg.det(tetm_r)
        t_arr_i = -4*P*tetm_i[0, 1]*tetm_i[1, 0]/np.linalg.det(tetm_i)

        try: 
            T = np.sqrt(max([t_arr_r, t_arr_i]))+.001
        except ValueError:
            T = 2
            
        sr = np.sqrt(T**2+4*P*tetm_r[0, 1]*tetm_r[1, 0]/np.linalg.det(tetm_r))
        si = np.sqrt(T**2+4*P*tetm_i[0, 1]*tetm_i[1, 0]/np.linalg.det(tetm_i))

        par_r = 2*tetm_r[0, 1]/(T-sr)
        orth_r = 2*tetm_r[1, 0]/(T+sr)
        par_i = 2*tetm_i[0, 1]/(T-si)
        orth_i = 2*tetm_i[1, 0]/(T+si)

        mat2_r = np.matrix([[0, 1./orth_r], [1./par_r, 0]])
        mat2_i = np.matrix([[0, 1./orth_i], [1./par_i ,0]])
        
        avg_mat = np.mean(np.array([np.dot(tetm_r, mat2_r),
                                    np.dot(tetm_i, mat2_i)]),
                          axis=0)
                                    
        dis[idx] = avg_mat
    
        if err_arr is not None:
            #find errors of entries for calculating weights
            sigma_sr = np.sqrt((-(2*P*tetm_r[0,1]*tetm_r[1,0]*\
                                  tetm_r[1,1]*err_arr[0,0])/\
                                  (np.linalg.det(tetm_r)**2*sr))**2+\
                                ((2*P*tetm_r[0,0]*tetm_r[1,0]*\
                                 tetm_r[1,1]*err_arr[0,1])/\
                                (np.linalg.det(tetm_r)**2*sr))**2+\
                                ((2*P*tetm_r[0,0]* tetm_r[0,1]*\
                                  tetm_r[1,1]*err_arr[1,0])/\
                                  (np.linalg.det(tetm_r)**2*sr))**2 +\
                                (-(2*P*tetm_r[0,1]* tetm_r[1,0]*\
                                 tetm_r[0,0]*err_arr[1,1])/\
                                 (np.linalg.det(tetm_r)**2*sr))**2)

            sigma_dr_11 = 0.5*sigma_sr
            sigma_dr_22 = 0.5*sigma_sr

            sigma_dr_12 = np.sqrt((mat2_r[0,1]/tetm_r[0,0]*err_arr[0,0])**2+\
                                  (mat2_r[0,1]/tetm_r[1,0]*err_arr[1,0])**2+\
                                  (0.5*tetm_r[0,0]/tetm_r[1,0]*sigma_sr)**2)
            sigma_dr_21 = np.sqrt((mat2_r[1,0]/tetm_r[1,1]*err_arr[1,1])**2+\
                                  (mat2_r[1,0]/tetm_r[0,1]*err_arr[0,1])**2+\
                                  (0.5*tetm_r[1,1]/tetm_r[0,1]*sigma_sr)**2)

            dis_err_r = np.array([[sigma_dr_11, sigma_dr_12],
                                  [sigma_dr_21, sigma_dr_22]])

            sigma_si = np.sqrt((-(2*P*tetm_i[0,1]*tetm_i[1,0]*\
                                  tetm_i[1,1]*err_arr[0,0])/\
                                  (np.linalg.det(tetm_i)**2*sr))**2+\
                                 ((2*P*tetm_i[0,0]*tetm_i[1,0]*\
                                  tetm_i[1,1]*err_arr[0,1])/\
                                  (np.linalg.det(tetm_i)**2*sr))**2+\
                                 ((2*P*tetm_i[0,0]*tetm_i[0,1]*\
                                  tetm_i[1,1]*err_arr[1,0])/\
                                  (np.linalg.det(tetm_i)**2*sr))**2+\
                                 (-(2*P*tetm_i[0,1]*tetm_i[1,0]*\
                                  tetm_i[0,0]*err_arr[1,1])/\
                                  (np.linalg.det(tetm_i)**2*sr))**2)

            sigma_di_11 = 0.5*sigma_si
            sigma_di_22 = 0.5*sigma_si
            sigma_di_12 = np.sqrt((mat2_i[0,1]/tetm_i[0,0]*err_arr[0,0])**2+\
                                  (mat2_i[0,1]/tetm_i[1,0]*err_arr[1,0])**2+\
                                  (0.5*tetm_i[0,0]/tetm_i[1,0]*sigma_si)**2)
            sigma_di_21 = np.sqrt((mat2_i[1,0]/tetm_i[1,1]*err_arr[1,1])**2+\
                                  (mat2_i[1,0]/tetm_i[0,1]*err_arr[0,1])**2+\
                                  (0.5*tetm_i[1,1]/tetm_i[0,1]*sigma_si)**2)

            dis_err_i = np.array([[sigma_di_11, sigma_di_12],
                                  [sigma_di_21, sigma_di_22]])
                                  
            dis_err[idx] = np.mean(np.array([dis_err_r, dis_err_i]),
                                   axis=0)

    else:
        dis[idx] = np.identity(2)

nonzero_idx = np.array(list(set(np.nonzero(dis)[0])))

dis_avg, weights_sum = np.average(dis[nonzero_idx], 
                                  axis=0, 
                                  weights=(1./dis_err[nonzero_idx])**2, 
                                  returned=True)

dis_avg_err = np.sqrt(1./weights_sum)
                                      
d, new_z, new_z_err = mt1.Z.remove_distortion(dis_avg, 
                                              distortion_err_tensor=dis_avg_err)

new_z_err = np.nan_to_num(new_z_err)
new_z_err[np.where(new_z_err == 0.0)] = 1.0

mt1.Z.z = new_z
mt1.Z.z_err = new_z_err

#mt1.write_edi_file(r"c:\Users\jpeacock\Documents\ShanesBugs\HalfSpaceSQC\par10ew_dr.edi")
mt1.write_edi_file(edi_fn_dr)

#print 'Initial D = {0}'.format(D)
print 'Found   D = {0}'.format(d)

pm = mtplot.plot_multiple_mt_responses(fn_list=[edi_fn, edi_fn_dr], 
                                        plot_style='all', 
                                        plot_num=2,
                                        fig_size=[8, 6])
    
