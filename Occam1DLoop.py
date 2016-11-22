# -*- coding: utf-8 -*-
"""
Created on Tue Dec 03 10:56:33 2013

@author: jpeacock-pr
"""

import mtpy.modeling.occam1d as occam1d
import mtpy.core.edi as mtedi
import os

#==============================================================================
# Inputs
#==============================================================================
edi_path = r"d:\Peacock\MTData\EDI_Files\GeographicNorth"
save_path = r"c:\MinGW32-xy\Peacock\occam\MonoBasin\MT\Inversion1D"
occam_path = r"c:\MinGW32-xy\Peacock\occam\Occam1D.exe"

z1_thickness = 5
z_depth = 200000
z_target = 50000
n_layers = 50
res_err = 30
phase_err = 2.5
max_iter = 20

#==============================================================================
# loop over each edi inverting for TE and TM modes
#==============================================================================
edi_list = [os.path.join(edi_path, edi) for edi in os.listdir(edi_path)
            if edi.find('.edi')>0]

log_fid = file(os.path.join(save_path, 'Occam1DLog.log'), 'w')

for edi in edi_list:
    e1 = mtedi.Edi(edi)
    
    #--> write occam1d data file
    ocd = occam1d.Data()
    if not os.path.exists(os.path.join(save_path, e1.station)):
        os.mkdir(os.path.join(save_path, e1.station))
        
    #--> write occam1d model file
    ocm = occam1d.Model()
    ocm.n_layers = n_layers
    ocm.bottom_layer = z_depth
    ocm.z1_layer = z1_thickness
    ocm.target_depth = z_target
    
    #--> write occam1d startup files
    ocs = occam1d.Startup()    
    
    log_fid.write('{0}\n'.format('='*72))
    log_fid.write('{0}{1}{0}\n'.format(' '*25, e1.station))
    
    for mmode in ['TE', 'TM']:
        sv_path = os.path.join(save_path, e1.station, mmode)
        ocd.write_data_file(edi_file=edi, res_err=res_err, phase_err=phase_err, 
                            mode=mmode, save_path=sv_path)

        #--> write model file
        ocm.save_path = sv_path
        ocm.write_model_file()
        
        #--> write startup file
        ocs.save_path = sv_path
        ocs.data_fn = ocd.data_fn
        ocs.model_fn = ocm.model_fn
        ocs.max_iter = max_iter
        ocs.write_startup_file()

        #--> run occam1d
        occam1d.Run(startup_fn=ocs.startup_fn, occam_path=occam_path, 
                    mode=mmode) 
        
        try:            
            ocm.read_iter_file(os.path.join(sv_path, mmode+'_5.iter'))
            log_fid.write('    --> {0} Mode RMS = {1:.2f}\n'.format(mmode, 
                          float(ocm.itdict['Misfit Value'])))
        except IOError:
            log_fid.write('    *** {0} Mode DID NOT RUN PROPERLY CHECK FILES\n'.format(mmode))

log_fid.close()
        
