# -*- coding: utf-8 -*-
"""
Created on Thu Feb  6 14:50:23 2025

@author: jpeacock
"""

# =============================================================================
# Imports
# =============================================================================

# from mt_metadata.timeseries import Location
# from mt_metadata.transfer_functions.io.zonge.metadata import Header\
from mt_metadata.timeseries import Provenance
from mt_metadata.transfer_functions.tf import Station
from mt_metadata.transfer_functions.tf import TransferFunction

from mt_metadata import TF_EDI_CGG, TF_EDI_EMPOWER
from mt_metadata.transfer_functions.core import TF

# =============================================================================
# l = Location()
# h = Header()
# p = Provenance()
# s = Station()
a = TF()
a.read(TF_EDI_CGG)

s = Station()


b = TF()
b.read(TF_EDI_EMPOWER)
