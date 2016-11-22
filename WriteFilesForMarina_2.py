# -*- coding: utf-8 -*-
"""
Created on Wed Jan 22 08:54:15 2014

@author: jpeacock-pr
"""

import mtpy.core.edi as mtedi
import scipy.signal as sps
import os
import numpy as np
import mtpy.analysis.pt as mtpt

dirpath = r"c:\Users\jpeacock-pr\Documents\Paralana"
edipath_base = os.path.join(dirpath, 'Base')
edipath_inj = os.path.join(dirpath, 'Inj')

mks = (1, 3)
sv_path_base_m = os.path.join(dirpath, 'Base', 'Marina_Files_11') 
sv_path_inj_m = os.path.join(dirpath, 'Inj', 'Marina_Files_11')
sv_path_base = os.path.join(dirpath, 'Base', 'MedFilt_11') 
sv_path_inj = os.path.join(dirpath, 'Inj', 'MedFilt_11')

if not os.path.exists(sv_path_base):
    os.mkdir(sv_path_base)
if not os.path.exists(sv_path_inj):
    os.mkdir(sv_path_inj)
if not os.path.exists(sv_path_base_m):
    os.mkdir(sv_path_base_m)
if not os.path.exists(sv_path_inj_m):
    os.mkdir(sv_path_inj_m)
    
    
header_line = ['period', 'res_xy', 'res_xy_err', 'res_yx', 'res_yx_err', 
               'phase_xy', 'phase_xy_err', 'phase_yx', 'phase_yx_err']

header_line_pt = ['period', 'phi_min', 'phi_min_err', 'phi_max', 'phi_max_err',
                  'beta', 'beta_err']
    
#station_list = ['pb{0:02}c'.format(ii) for ii in range(1, 57)]
## E-W stations
station_list_ew = ['pb{0:02}c'.format(ii) for ii in range(44, 33, -1)]+\
               ['pb{0:02}c'.format(ii) for ii in range(23, 34, 1)]
## NS stations
station_list_ns = ['pb{0:02}c'.format(ii) for ii in range(11, 0, -1)]+\
               ['pb{0:02}c'.format(ii) for ii in range(12, 23, 1)]
station_list_ne = ['pb{0:02}c'.format(ii) for ii in [53, 52, 35, 51, 12, 11, 1,
                        23, 24, 48, 49, 50]]
station_list_nw = ['pb{0:02}c'.format(ii) for ii in [56, 55, 35, 54, 12, 11, 1,
                        23, 24, 25, 45, 46, 47]]
               
for slst in [station_list_ew, station_list_ns, station_list_ne, station_list_nw]:
    station_list = list(slst)           
    for station in slst:
        fn_base = os.path.join(edipath_base, station+'.edi')
        fn_inj = os.path.join(edipath_inj, station+'.edi')
        if os.path.isfile(fn_base) == False or os.path.isfile(fn_inj) == False:
            print station
            station_list.remove(station)

    ns = len(station_list)
    nf = 43 # number of frequencies
    
    z_base_arr = np.zeros((ns, nf, 2, 2), dtype='complex')
    z_inj_arr = np.zeros((ns, nf, 2, 2), dtype='complex')
    
    for ss, station in enumerate(station_list):
        fn_base = os.path.join(edipath_base, station+'.edi')
        fn_inj = os.path.join(edipath_inj, station+'.edi')
        if os.path.isfile(fn_base) == True and os.path.isfile(fn_inj) == True:
            edi_base = mtedi.Edi(fn_base)
            edi_inj = mtedi.Edi(fn_inj)
            z_err_base = np.sqrt(edi_base.Z.zerr.copy())
            z_err_inj = np.sqrt(edi_inj.Z.zerr.copy())
    
            #print z_err_base[0, 0, 1]        
            #compute a static shift correction
            sx = np.sqrt(np.mean(edi_base.Z.resistivity[0:15, 0, 1]/
                                 edi_inj.Z.resistivity[0:15, 0, 1]))
            sy = np.sqrt(np.mean(edi_base.Z.resistivity[0:15, 1, 0]/
                                 edi_inj.Z.resistivity[0:15, 1, 0]))
                                 
            #remove the static shift from the injection survey
            s, new_z = edi_inj.Z.no_ss(1/sx, 1/sy)
            edi_inj.Z.z = new_z
            
            #--> fill z arrays
            z_base_arr[ss, :, :, :] = edi_base.Z.z
            z_inj_arr[ss, :, :, :] = edi_inj.Z.z       
            
    #--> apply a spatial median filter
    for ii in range(2):
        for jj in range(2):
            z_base_arr[:, :, ii, jj].real = sps.medfilt2d(z_base_arr[:, :, ii, jj].real, 
                                                          kernel_size=mks)
            z_base_arr[:, :, ii, jj].imag = sps.medfilt2d(z_base_arr[:, :, ii, jj].imag, 
                                                          kernel_size=mks)
            z_inj_arr[:, :, ii, jj].real = sps.medfilt2d(z_inj_arr[:, :, ii, jj].real, 
                                                          kernel_size=mks)
            z_inj_arr[:, :, ii, jj].imag = sps.medfilt2d(z_inj_arr[:, :, ii, jj].imag, 
                                                          kernel_size=mks)
                                                         
    #--> rewrite files
    for ss, station in enumerate(station_list):
        fn_base = os.path.join(edipath_base, station+'.edi')
        fn_inj = os.path.join(edipath_inj, station+'.edi')                                      
        
        edi_base = mtedi.Edi(fn_base)
        edi_inj = mtedi.Edi(fn_inj)
        
        edi_base.Z.z = z_base_arr[ss]
        edi_inj.Z.z = z_inj_arr[ss]
        
        edi_base.Z.zerr = edi_base.Z.zerr**2
        edi_inj.Z.zerr = edi_inj.Z.zerr**2
        
        #--> rewrite the edi files to a file with added f in file name for filtered
        new_fn_base = os.path.join(sv_path_base, 
                                   os.path.basename(fn_base)[:-4]+'f.edi')
        new_fn_inj = os.path.join(sv_path_inj, 
                                  os.path.basename(fn_inj)[:-4]+'f.edi')
        edi_base.writefile(new_fn_base)
        edi_inj.writefile(new_fn_inj)
    
        
        #write Marina's format
        rp_lines_base = []
        rp_lines_base.append(''.join(['{0:^12}'.format(hh) 
                                      for hh in header_line]+['\n']))
        rp_lines_inj = []
        rp_lines_inj.append(''.join(['{0:^12}'.format(hh) 
                                      for hh in header_line]+['\n']))
                         
        pt_lines_base = []
        pt_lines_base.append(''.join(['{0:^12}'.format(hh) 
                                     for hh in header_line_pt]+['\n']))
        pt_lines_inj = []
        pt_lines_inj.append(''.join(['{0:^12}'.format(hh) 
                                     for hh in header_line_pt]+['\n']))
                         
        pt_base = mtpt.PhaseTensor(z_object=edi_base.Z)
        pt_inj = mtpt.PhaseTensor(z_object=edi_inj.Z)
        
        for ii, freq in enumerate(edi_base.Z.freq):
            rp_lines_base.append(''.join(['{0:>12}'.format(nn) for nn in 
                                        ['{0:+.4e}'.format(mm) for mm in 
                                        [1./freq, 
                                         edi_base.Z.resistivity[ii, 0, 1],
                                         edi_base.Z.resistivity_err[ii, 0, 1],
                                         edi_base.Z.resistivity[ii, 1, 0],
                                         edi_base.Z.resistivity_err[ii, 1, 0],
                                         edi_base.Z.phase[ii, 0, 1],
                                         edi_base.Z.phase_err[ii, 0, 1],
                                         edi_base.Z.phase[ii, 1, 0],
                                         edi_base.Z.phase_err[ii, 1, 0]]]]+
                                         ['\n']))
            
            rp_lines_inj.append(''.join(['{0:>12}'.format(nn) for nn in 
                                        ['{0:+.4e}'.format(mm) for mm in 
                                        [1./freq, 
                                         edi_inj.Z.resistivity[ii, 0, 1],
                                         edi_inj.Z.resistivity_err[ii, 0, 1],
                                         edi_inj.Z.resistivity[ii, 1, 0],
                                         edi_inj.Z.resistivity_err[ii, 1, 0],
                                         edi_inj.Z.phase[ii, 0, 1],
                                         edi_inj.Z.phase_err[ii, 0, 1],
                                         edi_inj.Z.phase[ii, 1, 0],
                                         edi_inj.Z.phase_err[ii, 1, 0]]]]+
                                         ['\n']))
                                         
            pt_lines_base.append(''.join(['{0:>12}'.format(nn) for nn in 
                                        ['{0:+.4e}'.format(mm) for mm in 
                                        [1./freq, 
                                         pt_base.phimin[0][ii],
                                         pt_base.phimin[1][ii],
                                         pt_base.phimax[0][ii],
                                         pt_base.phimax[1][ii],
                                         pt_base.beta[0][ii],
                                         pt_base.beta[1][ii]]]]+
                                         ['\n']))
                                         
            pt_lines_inj.append(''.join(['{0:>12}'.format(nn) for nn in 
                                        ['{0:+.4e}'.format(mm) for mm in 
                                        [1./freq, 
                                         pt_inj.phimin[0][ii],
                                         pt_inj.phimin[1][ii],
                                         pt_inj.phimax[0][ii],
                                         pt_inj.phimax[1][ii],
                                         pt_inj.beta[0][ii],
                                         pt_inj.beta[1][ii]]]]+
                                         ['\n']))
        #--> write files 
        rp_fn_base = os.path.join(sv_path_base_m, 
                                  edi_base.station+'_ResPhase.dat') 
        rp_fid_base = file(mtedi.MTfh.make_unique_filename(rp_fn_base), 'w')
        rp_fid_base.writelines(rp_lines_base)
        rp_fid_base.close()
        
        rp_fn_inj = os.path.join(sv_path_inj_m, 
                                        edi_inj.station+'_ResPhase.dat')
        rp_fid_inj = file(mtedi.MTfh.make_unique_filename(rp_fn_inj), 'w')
        rp_fid_inj.writelines(rp_lines_inj)
        rp_fid_inj.close()
        
        pt_fn_base = os.path.join(sv_path_base_m, 
                                        edi_base.station+'_PT.dat') 
        pt_fid_base = file(mtedi.MTfh.make_unique_filename(pt_fn_base), 'w')
        pt_fid_base.writelines(pt_lines_base)
        pt_fid_base.close()
        
        pt_fn_inj = os.path.join(sv_path_inj_m, 
                                        edi_inj.station+'_PT.dat')
        pt_fid_inj = file(mtedi.MTfh.make_unique_filename(pt_fn_inj), 'w')
        pt_fid_inj.writelines(pt_lines_inj)
        pt_fid_inj.close()
    #            

                         
        
        

        