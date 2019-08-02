# -*- coding: utf-8 -*-
"""
Created on Wed Jul 17 17:05:20 2019

@author: jpeacock
"""

# =============================================================================
# Imports
# =============================================================================
import logging
import os
import re
import glob
from pathlib import Path
import numpy as np

from ph5.core import experiment

# =============================================================================
# Begin tools
# =============================================================================

### Initialize a PH5 file
def initialize_ph5_file(ph5_fn):
    """Initialize a PH5 file given a file name.  This will build the 
    appropriate groups needed in a PH5 file.
    
    :param ph5_fn: full path to ph5 file to be created
    :type ph5_fn: string or Path
    
    :return: opened message
    :rtype: bool [True | False]
    
    :return: ph5_fn
    :rtype: string
    """
    
    ph5_path = Path(ph5_fn)
    
    ph5_obj = experiment.ExperimentGroup(nickname=ph5_path.name,
                                         currentpath=ph5_path.parent)
    ph5_obj.ph5open(True)
    ph5_obj.initgroup()
    ph5_obj.ph5close()
    
    print("Made PH5 File {0}".format(ph5_path))
    
    return str(ph5_path) 
 
### Add an array to a PH5 file
    
# =============================================================================
# Tests    
# =============================================================================
ph5_test_path = initialize_ph5_file(r"c:\Users\jpeacock\Documents\GitHub\PH5\ph5\test_data\test.ph5")


    