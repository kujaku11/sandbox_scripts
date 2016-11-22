# -*- coding: utf-8 -*-
"""
Remove 3D points from .edi files that will be run for a 2D inversion

Created on Thu Nov 03 11:37:23 2016

@author: jpeacock
"""

#==============================================================================
# Imports
#==============================================================================
# standard packages
import os

# 3rd party packages
import numpy as np
import mtpy.core.mt as mt
import mtpy.analysis.geometry as geometry

#==============================================================================
# Input variables
#==============================================================================
edi_path = r"c:\Users\jpeacock\Documents\ShanesBugs\Sev_MT_Final_ga\inv_edi_files"
skew_threshold = 3
ellip_threshold = 0.1

#==============================================================================
# Find and remove any '3d' points
#==============================================================================
# make a new folder to save files into                
save_path = os.path.join(edi_path, 'edited_no_3d')
if not os.path.exists(save_path):
    os.mkdir(save_path)

# get list of edi files
edi_list = [os.path.join(edi_path, edi) for edi in os.listdir(edi_path)
            if edi.endswith('.edi')]

# loop over each edi file in edi list and remove 3D data points
for edi in edi_list:
    mt_obj = mt.MT(edi)
    # estimate geometry, returned array gives 1, 2, 3 for dimensions
    dim_arr = geometry.dimensionality(z_object=mt_obj.Z,
                                      skew_threshold=skew_threshold,
                                      eccentricity_threshold=ellip_threshold)
    
    # get the index values where the data is larger than 2D
    index_3d = np.where(dim_arr > 2)
    
    print '-'*50
    print index_3d
    print '-'*50
    
    # set the values of 3D data points to 0 for both Z and Tipper
    mt_obj.Z.z[index_3d] = np.zeros((2,2), dtype=np.complex)
    mt_obj.Z.z_err[index_3d] = np.zeros((2,2), dtype=np.float)
    mt_obj.Tipper.tipper[index_3d] = np.zeros((1,2), dtype=np.complex)
    mt_obj.Tipper.tipper_err[index_3d] = np.zeros((1,2), dtype=np.float)
    
    # write new edi file
    mt_obj.write_edi_file(new_fn=os.path.join(save_path, 
                                              '{0}.edi'.format(mt_obj.station)))
    
    
