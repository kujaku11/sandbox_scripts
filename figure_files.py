# -*- coding: utf-8 -*-
"""
Created on Tue Jul 14 13:54:55 2015

@author: jpeacock
"""
import os
import subprocess

def pdf_file_reduce_size(input_fn, output_fn=None, crop=True):
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
        
    std_out = subprocess.check_call(['gs', '-sDEVICE=pdfwrite', 
                                     '-dCompatibilityLevel=1.4',
                                     '-dDownsampleColorImages=true',
                                     '-dColorImageResolution=300',
                                     '-dNOPAUSE',
                                     '-dQUIET',
                                     '-dBATCH',
                                     '-sOutputFile={0}'.format(output_fn),
                                     fn_crop])
    os.remove(fn_crop)
    if std_out == 0:
        print 'converted {0} to {1}'.format(fn_in, output_fn)
        os.chdir(current_dir)
        return output_fn
        
#fn = r"/mnt/hgfs/Google Drive/Mono_Basin/Proposed_LV_MT_2016_Wilderness.pdf"
#fn = r"/mnt/hgfs/TexDocs/Presentations/VH_2015/Peacock_Geothermal_Meeting_2015.pdf"
#fn = r"/mnt/hgfs/TexDocs/Figures/mb_paper_joint_interp_figure_darcy.pdf"
#fn = r"/mnt/hgfs/Google Drive-2/Mono_Lake_2015/mono_lake_proposal.pdf"
#fn = r"/mnt/hgfs/Google Drive-2/JVG/Peacock_etal_2015_revision_2_diff.pdf"
#fn = r"/mnt/hgfs/Google Drive/Antarctica/figures/figure_07.pdf"
#fn = r"/mnt/hgfs/jpeacock/Documents/LV/figures/mt_vs_foulger2003.pdf"
#fn = r"/mnt/hgfs/jpeacock/Documents/LV/Figures/lv_hill_slice_annotated.pdf"
#fn = r"/mnt/hgfs/jpeacock/Documents/TexDocs/Figures/lv_earthquake_map.pdf"
#new_fn = pdf_file_reduce_size(fn, crop=True)
#fn = r"/media/jpeacock/Elements/Peacock/PHD/TexDocs/Dissertation/MainDissertation.pdf"
#fn = r"/mnt/hgfs/jpeacock/Google Drive/Posters/MP_models.pdf"
#fn = r"/mnt/hgfs/jpeacock/Documents/Forms/DefensiveDriving2015.pdf"
fn = r"/mnt/hgfs/jpeacock/Documents/ClearLake/geysers_usgs_mt_sites_proposed.pdf"
new_fn = pdf_file_reduce_size(fn, crop=True)
