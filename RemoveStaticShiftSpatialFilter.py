# -*- coding: utf-8 -*-
"""
Created on Mon Aug 19 10:06:21 2013

@author: jpeacock-pr
"""

import mtpy.core.mt as mt
import os
import numpy as np
import mtpy.imaging.mtplot as mtplot



def remove_static_shift_spatial_filter(edi_fn, radius=1000, num_freq=20, 
                                       freq_skip=4, shift_tol=.15, plot=False):
                                           
    """
    Remove static shift from a station using a spatial median filter.  This 
    will look at all the edi files in the same directory as edi_fn and find
    those station within the given radius (meters).  Then it will find
    the medain static shift for the x and y modes and remove it, given that 
    it is larger than the shift tolerance away from 1.  A new edi file will
    be written in a new folder called SS.  
    
    Arguments
    -----------------
        **edi_fn** : string
                     full path to edi file to have static shift removed
                     
        **radius** : float
                     radius to look for nearby stations, in meters.
                     *default* is 1000 m
        
        **num_freq** : int
                       number of frequencies calculate the median static
                       shift.  This is assuming the first frequency is the 
                       highest frequency.  Cause usually highest frequencies 
                       are sampling a 1D earth.  *default* is 20
                       
        **freq_skip** : int
                        number of frequencies to skip from the highest 
                        frequency.  Sometimes the highest frequencies are 
                        not reliable due to noise or low signal in the AMT
                        deadband.  This allows you to skip those frequencies.
                        *default* is 4
        
        **shift_tol** : float
                        Tolerance on the median static shift correction.  If
                        the data is noisy the correction factor can be biased
                        away from 1.  Therefore the shift_tol is used to stop
                        that bias.  If 1-tol < correction < 1+tol then the
                        correction factor is set to 1.  *default* is 0.15
                        
        **plot** : [ True | False ]
                   Boolean to plot the corrected response against the
                   non-corrected response.  *default* is False
                        
    Returns
    ----------------
        **new_edi_fn_ss** : string
                            new path to the edi file with static shift removed
                            
        **shift_corrections** : (float, float)
                                static shift corrections for x and y modes
        
        **plot_obj** : mtplot.plot_multiple_mt_responses object
                       If plot is True a plot_obj is returned
                       If plot is False None is returned
    """
    
    # convert meters to decimal degrees so we don't have to deal with zone 
    # changes
    meter_to_deg_factor = 8.994423457456377e-06
    dm_deg = radius*meter_to_deg_factor

    # make a list of edi files in the directory
    edi_path = os.path.dirname(edi_fn)
    edi_list = [os.path.join(edi_path, edi) for edi in os.listdir(edi_path)
                if edi.find('.edi') > 0]
    edi_list.remove(edi_fn)
    
    # read the edi file
    mt_obj = mt.MT(edi_fn)
    mt_obj.Z._compute_res_phase()              
    
    # Find stations near by and store them in a list
    mt_obj_list = []
    for kk, kk_edi in enumerate(edi_list):
        mt_obj_2 = mt.MT(kk_edi)
        delta_d = np.sqrt((mt_obj.lat-mt_obj_2.lat)**2+\
                          (mt_obj.lon-mt_obj_2.lon)**2)
        if delta_d <= dm_deg:
            mt_obj_2.delta_d = float(delta_d)/meter_to_deg_factor
            mt_obj_list.append(mt_obj_2)
    
    # extract the resistivity values from the near by stations       
    res_array = np.zeros((len(mt_obj_list), num_freq, 2, 2))
    print 'These stations are within the given {0} m radius:'.format(radius)
    for kk, mt_obj_kk in enumerate(mt_obj_list):
        print '\t{0} --> {1:.1f} m'.format(mt_obj_kk.station, mt_obj_kk.delta_d)
        interp_freq = mt_obj.Z.freq[freq_skip:num_freq+freq_skip] 
        Z_interp, Tip_interp = mt_obj_kk.interpolate(interp_freq)
        Z_interp._compute_res_phase()
        res_array[kk, :, :, :] = Z_interp.resistivity[0:num_freq, :, :]
    
    #compute the static shift of x-components
    static_shift_x = mt_obj.Z.resistivity[freq_skip:num_freq+freq_skip, 0, 1]/\
                     np.median(res_array[:, :, 0, 1], axis=0)
    static_shift_x = np.median(static_shift_x)
    
    ##check to see if the estimated static shift is within given tolerance
    if 1-shift_tol < static_shift_x and static_shift_x < 1+shift_tol:
        static_shift_x = 1.0
    
    #compute the static shift of y-components
    static_shift_y = mt_obj.Z.resistivity[freq_skip:num_freq+freq_skip, 1, 0]/\
                     np.median(res_array[:, :, 1, 0], axis=0)
    static_shift_y = np.median(static_shift_y)
    
    ##check to see if the estimated static shift is within given tolerance
    if 1-shift_tol < static_shift_y and static_shift_y < 1+shift_tol:
        static_shift_y = 1.0
        
    print 'x static shift is {0:.3f}'.format(static_shift_x)
    print 'y static shift is {0:.3f}'.format(static_shift_y)
    
    s, z_ss = mt_obj.Z.no_ss(reduce_res_factor_x=static_shift_x, 
                             reduce_res_factor_y=static_shift_y)
    
    mt_obj.Z.z = z_ss
    new_edi_fn = os.path.join(edi_path, 'SS', '{0}_ss.edi'.format(mt_obj.station)) 
    mt_obj.write_edi_file(new_fn=new_edi_fn)
    
    if plot == True:
        rpm = mtplot.plot_multiple_mt_responses(fn_list=[edi_fn, new_edi_fn], 
                                                plot_style='compare')
        return new_edi_fn, s[0], rpm
    else:
        return new_edi_fn, s[0], None
        
sp_edi_path = r"d:\Peacock\MTData\SanPabloBay\EDI_Files_dp"
sp_edi_list = [os.path.join(sp_edi_path, sp_edi) for sp_edi in 
               os.listdir(sp_edi_path) if sp_edi.find('.edi') > 0]

n_edi_list = []
ss_list = []
for sp_edi in sp_edi_list:
    n_edi_fn, s_arr, p_dummy = remove_static_shift_spatial_filter(sp_edi)
    n_edi_list.append(n_edi_fn)
    ss_list.append(s_arr)