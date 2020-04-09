# -*- coding: utf-8 -*-
"""
Created on Tue Jul 14 13:54:55 2015

@author: jpeacock
"""
import os
import subprocess

def pdf_file_reduce_size(input_fn, output_fn=None, crop=True, gs_exe='gs'):
    current_dir = os.getcwd()
    dir_path = os.path.abspath(os.path.dirname(input_fn))
    os.chdir(dir_path)
    
    fn_in = os.path.basename(input_fn)
    
    if output_fn is None:
        output_fn = '{0}_small.pdf'.format(fn_in[:-4])
        
    if crop is True:
        fn_crop = '{0}_crop0.pdf'.format(fn_in[:-4])
        std_out = subprocess.check_call(['pdfcrop', fn_in, fn_crop])
    else:
        fn_crop = fn_in
        
    std_out = subprocess.check_call([gs_exe, '-sDEVICE=pdfwrite', 
                                     '-dCompatibilityLevel=1.4',
                                     '-dDownsampleColorImages=true',
                                     '-dColorImageResolution=300',
                                     '-dNOPAUSE',
                                     '-dQUIET',
                                     '-dBATCH',
                                     '-sOutputFile={0}'.format(output_fn),
                                     fn_crop])
    if crop:
        os.remove(fn_crop)
    if std_out == 0:
        print('converted {0} to {1}'.format(fn_in, output_fn))
        os.chdir(current_dir)
        return output_fn
        
for fn in [r"c:\Users\jpeacock\OneDrive - DOI\Geysers\jvgr\gz_pt_summary.pdf"]:

    new_fn = pdf_file_reduce_size(fn, crop=False, 
                                  gs_exe="gswin64c")
