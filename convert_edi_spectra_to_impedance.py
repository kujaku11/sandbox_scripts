# -*- coding: utf-8 -*-
"""
Convert spectra data to impedance

Created on Fri Aug  3 09:31:58 2018

@author: jpeacock
"""

import os
import mtpy.core.mt as mt
import mtpy.usgs.usgs_archive as archive

# =============================================================================
# Inputs 
# =============================================================================
edi_path = r"c:\Users\jpeacock\Documents\edi_folders\br_bodie_2017"
location_csv = r"c:\Users\jpeacock\Documents\edi_folders\br_bodie_2017\Mono Basin WGS84.txt"

# =============================================================================
# make parameters
# =============================================================================
sv_path = os.path.join(edi_path, 'Impedance')
if not os.path.exists(sv_path):
    os.mkdir(sv_path)
    
edi_list = [os.path.join(edi_path, edi) for edi in os.listdir(edi_path)
             if edi.endswith('.edi')]

s_dict = {}
with open(location_csv, 'r') as fid:
    lines = fid.readlines()

ab_dict = {'A':100, 'B':200, 'C':300, 'D':400, 'E':500, 'F':600, 'G':700}

for line in lines[2:]:
    line_list = line.split()
    if len(line_list) != 3:
        continue
    line_list = [l.strip() for l in line_list]
    s_label = line_list[0][0]
    s_number = int(line_list[0][1:].replace('.', ''))
    if s_number < 10:
        s_number *= 10
    s = '{0}'.format(ab_dict[s_label]+s_number)
    s_dict[s] = {'station':line_list[0],
                 'lat':float(line_list[1]),
                 'lon':float(line_list[2])}

# =============================================================================
# Loop over edi files and make impedance
# =============================================================================
for edi_fn in edi_list:
    st_dict = s_dict[os.path.basename(edi_fn)[0:-4]]
    mt_obj = mt.MT(edi_fn)
    mt_obj.station = st_dict['station']
    mt_obj.lat = st_dict['lat']
    mt_obj.lon = st_dict['lon']
    mt_obj.elev = archive.get_nm_elev(st_dict['lat'], st_dict['lon'])
    mt_obj.write_mt_file(save_dir=sv_path)
    p = mt_obj.plot_mt_response(plot_num=2)
    p.save_plot(os.path.join(sv_path, mt_obj.station+'.png'), fig_dpi=600)