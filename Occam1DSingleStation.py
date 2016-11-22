# -*- coding: utf-8 -*-
"""
Created on Fri Jan 17 09:57:36 2014

@author: jpeacock-pr
"""

import os
import mtpy.modeling.occam1d as occam1d


#==============================================================================
# Inputs
#==============================================================================
edi_path = r"c:\MinGW32-xy\Peacock\wsinv3d\MB_MT\EDI_1DInversions\EDI_Files"
station = 'MB150'
edi = os.path.join(edi_path, station+'.edi')
if os.path.isfile(edi) == False:
    print 'Did not find {0}, check path'.format(edi)

save_dir = os.path.dirname(edi_path)
opath = 'c:\\MinGW32-xy\\Peacock\\occam\\occam1d.exe'
iter_num = 6 
z1_thickness = 5
z_depth = 200000
n_layers = 50
res_err = 30
phase_err = 2.5
max_iter = 10

invert = 'y'
plot = 'y'
plot_save = 'y'

#==============================================================================
if invert == 'y':
     #--> write occam1d data file             
    ocd = occam1d.Data()
    ocd.save_path = os.path.join(save_dir, station)
    ocd.write_data_file(edi_file=edi, mode='TM', res_err=10, phase_err=2.5)
    data_tm_fn = ocd.data_fn    
    ocd.write_data_file(edi_file=edi, mode='TE', res_err=10, phase_err=2.5)
    data_te_fn = ocd.data_fn
    
    #--> write occam1d model file
    ocm = occam1d.Model()
    ocm.save_path = ocd.save_path
    ocm.n_layers = n_layers
    ocm.bottom_layer = z_depth
    ocm.z1_layer = z1_thickness
    ocm.write_model_file()
    
    #--> write occam1d startup file
    ocs = occam1d.Startup()
    ocs.data_fn = data_tm_fn
    ocs.model_fn = ocm.model_fn
    ocs.save_path = ocd.save_path
    ocs.max_iter = max_iter
    ocs.rough_type = 4
    ocs.debug_level = 2
    ocs.min_max_bounds = (-3, 4) 
    ocs.write_startup_file()
    
    #--> run occam1d
    occam1d.Run(ocs.startup_fn, occam_path=opath, mode='TM')
    
    #--> write occam1d startup file
    ocs = occam1d.Startup()
    ocs.data_fn = data_te_fn
    ocs.model_fn = ocm.model_fn
    ocs.save_path = ocd.save_path
    ocs.max_iter = max_iter
    ocs.rough_type = 4
    ocs.debug_level = 2
    ocs.min_max_bounds = (-3, 5)
    ocs.write_startup_file()
    occam1d.Run(ocs.startup_fn, occam_path=opath, mode='TE')

if plot == 'y':
    try:
        resp_tm_list = [os.path.join(save_dir, station, 'TM_{0}.resp'.format(rr))
                     for rr in range(1, iter_num+1)]
        iter_tm_list = [os.path.join(save_dir, station, 'TM_{0}.iter'.format(rr))
                     for rr in range(1, iter_num+1)]
        resp_te_list = [os.path.join(save_dir, station, 'TE_{0}.resp'.format(rr))
                     for rr in range(1, iter_num+1)]
        iter_te_list = [os.path.join(save_dir, station, 'TE_{0}.iter'.format(rr))
                     for rr in range(1, iter_num+1)]
        model_fn = os.path.join(ocd.save_path, 'Model1D')
        
        p1 = occam1d.Plot1DResponse(data_tm_fn=data_tm_fn,
                                    data_te_fn=data_te_fn,
                                    model_fn=model_fn,
                                    resp_tm_fn=resp_tm_list[-1],
                                    iter_tm_fn=iter_tm_list[-1],
                                    resp_te_fn=resp_te_list[-1],
                                    iter_te_fn=iter_te_list[-1],
                                    depth_limits=(0, 50),
                                    title_str=station)
        if plot_save == 'y':                            
            sv_path = os.path.join(save_dir, 'Plots', station+'.png')
            p1.save_figure(sv_path, fig_dpi=600, close_plot='n')
    except IOError:
        print '{0} did not run properly, check occam1d files'.format(station)
    
