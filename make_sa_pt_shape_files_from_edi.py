# -*- coding: utf-8 -*-
"""
Created on Fri Nov 07 09:15:17 2014

@author: jpeacock-pr
"""

import mtpy.utils.shapefiles as shapefiles
import os

edi_path = r"c:\Users\jpeacock\Documents\SaudiArabia\EDI_Files\GeographicNorth\Interpolated"
edi_list = [os.path.join(edi_path, edi_fn) for edi_fn in os.listdir(edi_path)
            if edi_fn.endswith('.edi')]

save_path = r"c:\Users\jpeacock\Documents\SaudiArabia\GIS"
map_projection = 'WGS84'
theta_r = 0

def check_dir(directory_path):
    if os.path.isdir(directory_path) is False:
        os.mkdir(directory_path)
        print 'Made directory {0}'.format(directory_path)
        
#-----------------------------------------------------------
#--> write phase tensor shape files
pts = shapefiles.PTShapeFile(edi_list=edi_list)
pts.projection = map_projection
pts.ellipse_size = 2800
pts.save_path = os.path.join(save_path, 'SA_PT_GN')
check_dir(pts.save_path)
pts.write_shape_files()

#----------------------------------------------------------------
#--> write tipper information
tps = shapefiles.TipperShapeFile(edi_list=edi_list)
tps.arrow_size = 20000
tps.arrow_head_height = 350
tps.arrow_head_width = 200
tps.arrow_lw = 100
tps.projection = map_projection
tps.save_path = os.path.join(save_path, 'SA_TIP_GN')
check_dir(tps.save_path)
tps.write_imag_shape_files()
tps.write_real_shape_files()