# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 16:04:15 2015

@author: jpeacock
"""

import os
import subprocess

#dir_path = r"/mnt/hgfs/TexDocs/Figures"

dir_path = r"/mnt/hgfs/Google Drive/JVG"
os.chdir(dir_path)

fn_list = ['mb_base_map_plutons_bw_03.pdf', 
           'mb_resistivities_plot.pdf',
           'Magma_bailey_example_with_map.pdf',
           'melt_resistivity.pdf',
           'mb_paper_pt_figure_rot.pdf',
           'mb_paper_joint_interp_figure.pdf',
           'mb_profile_lines_all.pdf',
           'mb_3d_cartoon.pdf']
           
#fn_list = [fn for fn in os.listdir(dir_path) if fn.find('lv_res_map') == 0 and 
#            fn[-4:] == '.pdf']

for ii, fn in enumerate([fn_list[4]], 5):
#    fn_out = 'figure_{0:02}_600_dpi.jpg'.format(ii)
#    std_out = subprocess.check_call(['convert', '-density', '600', '-trim',
#                                     fn, fn_out])
#                                     
#    if std_out == 0:
#        print 'converted {0} to {1}'.format(fn, fn_out)
    
#    fn_out = 'figure_{0:02}.eps'.format(ii)
#    fn_crop = '{0}_crop.pdf'.format(fn[:-4])
#    std_out = subprocess.check_call(['pdfcrop', fn, fn_crop])
#    std_out = subprocess.check_call(['pdftops', '-eps', '-level3', 
#                                     fn_crop, fn_out])
#    os.remove(fn_crop)
#    if std_out == 0:
#        print 'converted {0} to {1}'.format(fn, fn_out)
        
    fn_out = 'figure_{0:02}.pdf'.format(ii)
    fn_crop = '{0}_crop0.pdf'.format(fn[:-4])
    std_out = subprocess.check_call(['pdfcrop', fn, fn_crop])
    std_out = subprocess.check_call(['gs', '-sDEVICE=pdfwrite', 
                                     '-dCompatibilityLevel=1.4',
                                     '-dDownsampleColorImages=true',
                                     #'-dColorImageResolution=300',
                                     '-dNOPAUSE',
                                     '-dQUIET',
                                     '-dBATCH',
                                     '-sOutputFile={0}'.format(fn_out),
                                     fn_crop])
    os.remove(fn_crop)
    if std_out == 0:
        print 'converted {0} to {1}'.format(fn, fn_out)