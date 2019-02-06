# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 16:16:13 2018

@author: jpeacock
"""

import os
import mtpy.core.mt as mt

edi_path = r"c:\Users\jpeacock\Documents\MountainPass\EDI_Files_birrp\Edited\geographic_north"

zonge_cfg = r"D:\Peacock\MTData\MountainPass\mp_zonge.cfg"
birrp_cfg = r"D:\Peacock\MTData\MountainPass\mp_zonge.cfg"


sv_path = os.path.join(edi_path, 'final_edi')
png_path = os.path.join(edi_path, 'final_png')
if not os.path.exists(sv_path):
    os.mkdir(sv_path)
if not os.path.exists(png_path):
    os.mkdir(png_path)
    
for fn in os.listdir(edi_path):
    if not fn.endswith('.edi'):
        continue
    if 'mp1' in fn:
        continue
#        mt_obj = mt.MT(fn=os.path.join(edi_path, fn))
#        mt_obj.station = fn[0:5]
#        mt_obj.Notes.info_list = mt_obj.Notes.info_list[25:]
#        mt_obj.Notes.info_dict = {}
#        for info_str in mt_obj.Notes.info_list:
#            key, value = info_str.split(':', 1)
#            if key in ['notes', 'save_path', 'sampling_interval', 'station', 
#                       'ts.number', 'ts.t0error', 'ts.t0offset', 'setup.number', 
#                       'mtft.tsplot.pntrange', 'station_type', 'ts.frqband']:
#                continue
#            if 'phaseslope' in key:
#                key  = 'mtft.'+key
#            mt_obj.Notes.info_dict[key.strip()] = value.strip()
#        mt_obj.read_cfg_file(zonge_cfg)
#        mt_obj.Copyright.Citation.author = ','.join(mt_obj.Copyright.Citation.author)
#        mt_obj.Copyright.Citation.title = ','.join(mt_obj.Copyright.Citation.title)
#        mt_obj.write_mt_file(save_dir=sv_path)
    else:
        mt_obj = mt.MT(fn=os.path.join(edi_path, fn))
        birrp_index = mt_obj.Notes.info_list.index('BIRRP Parameters')+1
        mt_obj.Notes.info_list = mt_obj.Notes.info_list[birrp_index:]
        mt_obj.Notes.info_dict = {}
        for info_str in mt_obj.Notes.info_list:
            key, value = info_str.split(':', 1)
            if key in ['n_samples', 'ofil', 'prej']:
                continue
            else:
                key = 'birrp.{0}'.format(key)
            mt_obj.Notes.info_dict[key.strip()] = value.strip()
        mt_obj.read_cfg_file(birrp_cfg)
        mt_obj.Copyright.Citation.author = ','.join(mt_obj.Copyright.Citation.author)
        mt_obj.Copyright.Citation.title = ','.join(mt_obj.Copyright.Citation.title)
        mt_obj.write_mt_file(save_dir=sv_path)
    
    # plot response
    pr = mt_obj.plot_mt_response(plot_num=2)
    pr.save_plot(os.path.join(png_path, mt_obj.station+'.png'), fig_dpi=300)
            
            