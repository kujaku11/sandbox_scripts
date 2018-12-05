#! /usr/bin/env python
"""
Description:
    Example python script
    plot 3D penetration depth for a folder of EDI files

    input = path2edifolder

CreationDate:   23/03/2018
Developer:      fei.zhang@ga.gov.au

Revision History:
    LastUpdate:     23/03/2018   FZ
    LastUpdate:     23/10/2018   FZ

"""
import glob
import os
import sys

from mtpy.core.edi_collection import EdiCollection
from mtpy.imaging import penetration_depth3d as pen3d

# =============================================================================
# Inputs
# =============================================================================
# change the variable below according to your edi files folder
edidir = r'c:\Users\jpeacock\Documents\ClearLake\EDI_Files_birrp\Edited'  
savepath = r'c:\Users\jpeacock\Documents\ClearLake'


if not os.path.isdir(edidir):
    print("please provide the path to edi folder")
    sys.exit(1)

edifiles = glob.glob(os.path.join(edidir, "*.edi"))

# Create plot for a period index number 1,2,3 ..., 10 for determinant. This may not make sense sometimes.
# change to your preferred file resolution
#pen3d.plot_latlon_depth_profile(edidir, 4, 'det', showfig=True, savefig=True, 
#                                savepath=savepath, fig_dpi=400)

# The recommended way is to use a float value for the period.

#############################################################
# More Stats analysis on the EDI files periods

edis_obj = EdiCollection(edilist=edifiles)
edis_obj.select_periods(percentage=5.0)

per_freq = edis_obj.get_periods_by_stats(percentage=80.0)

for aper in range(-15, 0, -1):
    pen3d.plot_bar3d_depth(edidir, aper)
#    pen3d.plot_latlon_depth_profile(edidir, aper, showfig=True, savefig=True,
#                                    savepath=savepath,
#                                    fig_dpi=600)