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
edipath_inj = os.path.join(dirpath, 'Post')

ks = (3, 5)
mb = 1.05
mi = .95

sv_path_base_m = os.path.join(dirpath, 'Base', 'Marina_Files') 
sv_path_inj_m = os.path.join(dirpath, 'Post', 'Marina_Files')
sv_path_base = os.path.join(dirpath, 'Base', 'MedFilt_2') 
sv_path_inj = os.path.join(dirpath, 'Post', 'MedFilt_2')

if not os.path.exists(sv_path_base):
    os.mkdir(sv_path_base)
if not os.path.exists(sv_path_inj):
    os.mkdir(sv_path_inj)
if not os.path.exists(sv_path_base_m):
    os.mkdir(sv_path_base_m)
if not os.path.exists(sv_path_inj_m):
    os.mkdir(sv_path_inj_m)
    
    
#slst = ['pb{0:02}c'.format(ii) for ii in range(1, 57)]
## E-W stations
#slst = ['pb{0:02}'.format(ii) for ii in range(44, 33, -1)]+\
#        ['pb{0:02}'.format(ii) for ii in range(23, 34, 1)]
## N-S stations
slst = ['pb{0:02}'.format(ii) for ii in range(11, 0, -1)]+\
       ['pb{0:02}'.format(ii) for ii in range(12, 23, 1)]
        
##slst = ['pb{0:02}'.format(ii) for ii in [52, 51, 4, 48, 25, 49, 50]]
#slst = ['pb{0:02}'.format(ii) for ii in [56, 55, 54, 4, 45, 25, 46, 47]]
                  
station_list = list(slst)           
for station in slst:
    fn_base = os.path.join(edipath_base, station+'.edi')
    fn_inj = os.path.join(edipath_inj, station+'.edi')
    if os.path.isfile(fn_base) == False or os.path.isfile(fn_inj) == False:
        print station
        station_list.remove(station)
                  
header_line = ['period', 'res_xy', 'res_xy_err', 'res_yx', 'res_yx_err', 
               'phase_xy', 'phase_xy_err', 'phase_yx', 'phase_yx_err']

header_line_pt = ['period', 'phi_min', 'phi_min_err', 'phi_max', 'phi_max_err',
                  'beta', 'beta_err']

ns = len(station_list)
nf = 43 # number of frequencies
res_array_base = np.zeros((ns, nf, 2, 2))
res_array_inj = np.zeros((ns, nf, 2, 2))
phase_array_base = np.zeros((ns, nf, 2, 2))
phase_array_inj = np.zeros((ns, nf, 2, 2))

for ii, ss in enumerate(station_list):
    fn_base = os.path.join(edipath_base, ss+'.edi')
    fn_inj = os.path.join(edipath_inj, ss+'.edi')
    if os.path.isfile(fn_base) == True and os.path.isfile(fn_inj) == True:
        edi_base = mtedi.Edi(fn_base)
        edi_inj = mtedi.Edi(fn_inj)
        edi_base.Z.z = edi_base.Z.z
        edi_inj.Z.z = edi_inj.Z.z
        z_err_base = np.sqrt(edi_base.Z.zerr.copy())
        z_err_inj = np.sqrt(edi_inj.Z.zerr.copy())

        #print z_err_base[0, 0, 1]        
        #compute a static shift correction
        sx = np.sqrt(np.mean(edi_base.Z.resistivity[0:15, 0, 1]/
                             edi_inj.Z.resistivity[0:15, 0, 1]))
        sy = np.sqrt(np.mean(edi_base.Z.resistivity[0:15, 1, 0]/
                             edi_inj.Z.resistivity[0:15, 1, 0]))
                             
        #------median filter the response---------
        res_base = edi_base.Z.resistivity.copy()
        res_inj = edi_inj.Z.resistivity.copy()
        phase_base = edi_base.Z.phase.copy()
        phase_inj = edi_inj.Z.phase.copy()
        
        res_inj[:, 0, 0] = res_inj[:, 0, 0]*sx**2
        res_inj[:, 0, 1] = res_inj[:, 0, 1]*sx**2
        res_inj[:, 1, 0] = res_inj[:, 1, 0]*sy**2
        res_inj[:, 1, 1] = res_inj[:, 1, 1]*sy**2
        
        res_base[:, 0, 0] *= mb
        res_inj[:, 0, 0] = mi*res_inj[:, 0, 0]+.05*res_inj[0, 0, 0]
        res_base[:, 0, 1] *= mb
        res_inj[:, 0, 1] = mi*res_inj[:, 0, 1]+.05*res_inj[0, 0, 1]
        res_base[:, 1, 0] *= mb
        res_inj[:, 1, 0] = mi*res_inj[:, 1, 0]+.05*res_inj[0, 1, 0]
        res_base[:, 1, 1] *= mb
        res_inj[:, 1, 1] = mi*res_inj[:, 1, 1]+.05*res_inj[0, 1, 1]
        
        phase_base[:, 0, 0] *= mb
        phase_inj[:, 0, 0] = mi*phase_inj[:, 0, 0]+.05*phase_inj[:, 0, 0]
        phase_base[:, 0, 0] -= abs(edi_base.Z.phase[0, 0, 0]-phase_base[0, 0, 0])        
        phase_inj[:, 0, 0] -= abs(edi_inj.Z.phase[0, 0, 0]-phase_inj[0, 0, 0])
        
        phase_base[:, 0, 1] *= mb
        phase_inj[:, 0, 1] = mi*phase_inj[:, 0, 1]+.05*phase_inj[:, 0, 1]
        phase_base[:, 0, 1] -= abs(edi_base.Z.phase[0, 0, 1]-phase_base[0, 0, 1])        
        phase_inj[:, 0, 1] -= abs(edi_inj.Z.phase[0, 0, 1]-phase_inj[0, 0, 1])        
        
        phase_base[:, 1, 0] *= mb
        phase_inj[:, 1, 0] = mi*phase_inj[:, 1, 0]+.05*phase_inj[:, 1, 0]
        phase_base[:, 1, 0] += abs(edi_base.Z.phase[0, 1, 0]-phase_base[0, 1, 0])        
        phase_inj[:, 1, 0] += abs(edi_inj.Z.phase[0, 1, 0]-phase_inj[0, 1, 0])
        
        phase_base[:, 1, 1] *= mb
        phase_inj[:, 1, 1] = mi*phase_inj[:, 1, 1]+.05*phase_inj[:, 1, 1]
        phase_base[:, 1, 1] += abs(edi_base.Z.phase[0, 1, 1]-phase_base[0, 1, 1])        
        phase_inj[:, 1, 1] += abs(edi_inj.Z.phase[0, 1, 1]-phase_inj[0, 1, 1])
        
        res_array_base[ii, :, :, :] = res_base
        res_array_inj[ii, :, :, :] = res_inj
        phase_array_base[ii, :, :, :] = phase_base
        phase_array_inj[ii, :, :, :] = phase_inj
#
for ii in range(2):
    for jj in range(2):
        res_array_base[:, :, ii, jj] = sps.medfilt2d(res_array_base[:, :, ii, jj],
                                                     ks)
        res_array_inj[:, :, ii, jj] = sps.medfilt2d(res_array_inj[:, :, ii, jj],
                                                     ks)
        phase_array_base[:, :, ii, jj] = sps.medfilt2d(phase_array_base[:, :, ii, jj],
                                                     ks)
        phase_array_inj[:, :, ii, jj] = sps.medfilt2d(phase_array_inj[:, :, ii, jj],
                                                     ks)

#write edi and marina files
for ii, ss in enumerate(station_list):
    fn_base = os.path.join(edipath_base, ss+'.edi')
    fn_inj = os.path.join(edipath_inj, ss+'.edi')
    if os.path.isfile(fn_base) == True and os.path.isfile(fn_inj) == True:
        edi_base = mtedi.Edi(fn_base)
        edi_inj = mtedi.Edi(fn_inj)
        
        
        #--> set new values
        edi_base.Z.set_res_phase(res_array_base[ii], phase_array_base[ii])
        edi_base.Z.zerr = .1*edi_base.Z.zerr.copy()**2
        
        edi_inj.Z.set_res_phase(res_array_inj[ii], phase_array_inj[ii])
        edi_inj.Z.zerr = .1*edi_inj.Z.zerr.copy()**2

        
        new_fn_base = os.path.join(sv_path_base, 
                                   os.path.basename(fn_base)[:-4]+'f.edi')
        new_fn_inj = os.path.join(sv_path_inj, 
                                  os.path.basename(fn_inj)[:-4]+'f.edi')
                                  
        edi_base.writefile(new_fn_base)
        edi_inj.writefile(new_fn_inj)
#        
#        #pc = mtplot.plot_multiple_mt_responses(fn_list=[new_fn_base, new_fn_inj],
#        #                                       plot_style='compare')
#        
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
                                         edi_base.Z.phase[ii, 1, 0]-180,
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
                                         edi_inj.Z.phase[ii, 1, 0]-180,
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
        rp_fid_base = file(os.path.join(sv_path_base_m, 
                                        edi_base.station+'_ResPhase.dat'), 'w')
        rp_fid_base.writelines(rp_lines_base)
        rp_fid_base.close()
        
        rp_fid_inj = file(os.path.join(sv_path_inj_m, 
                                        edi_inj.station+'_ResPhase.dat'), 'w')
        rp_fid_inj.writelines(rp_lines_inj)
        rp_fid_inj.close()
        
        pt_fid_base = file(os.path.join(sv_path_base_m, 
                                        edi_base.station+'_PT.dat'), 'w')
        pt_fid_base.writelines(pt_lines_base)
        pt_fid_base.close()
        
        pt_fid_inj = file(os.path.join(sv_path_inj_m, 
                                        edi_inj.station+'_PT.dat'), 'w')
        pt_fid_inj.writelines(pt_lines_inj)
        pt_fid_inj.close()
#            

                         
        
        

        