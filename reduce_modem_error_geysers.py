# -*- coding: utf-8 -*-
"""
Created on Mon Aug 28 11:56:04 2017

@author: jpeacock
"""

import mtpy.modeling.modem as modem

dfn_07 = r"c:\Users\jpeacock\Documents\ClearLake\modem_inv\inv02_dr\gz_data_err07_elev_c_dr.dat"
dfn_03 = r"C:\Users\jpeacock\Documents\ClearLake\modem_inv\inv04\geysers_modem_data_err03.dat"
# dfn_03 = r"C:\Users\jpeacock\Documents\ClearLake\modem_inv\inv02_dr\geysers_modem_data_err03.dat"


d_07 = modem.Data()
d_07.read_data_file(dfn_07)

d_03 = modem.Data()
d_03.read_data_file(dfn_03)

d_03.station_locations = d_07.station_locations

d_03.write_data_file(
    fn_basename="gz_data_err03_ec_dr.dat",
    fill=False,
    compute_error=False,
    elevation=True,
)
