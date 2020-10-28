# -*- coding: utf-8 -*-
"""
Created on Thu May 05 17:55:04 2016

@author: jpeacock
"""

import mtpy.modeling.modem_new as modem
import numpy as np

# data_fn = r"c:\Users\jpeacock\Documents\Montserrat\Mont_no_elevation.dat"
#
# d_obj = modem.Data()
# d_obj.read_data_file(data_fn)
#
# cp_arr = d_obj.data_array[np.where(d_obj.data_array['station']=='MMT12')]
# cp_east = cp_arr['rel_east'][0]
# cp_north = cp_arr['rel_north'][0]
#
# d_obj.data_array['rel_east'][:] -= cp_east
# d_obj.data_array['rel_north'][:] -= cp_north
#
# d_obj.write_data_file(fn_basename='mont_no_topo_shift.dat',
#                      compute_error=False,
#                      fill=False)

inv01_dfn = r"c:\Users\jpeacock\Documents\Montserrat\Inv01_topo\Mont_data_elev.dat"
inv02_dfn = (
    r"c:\Users\jpeacock\Documents\Montserrat\Inv02_topo\mont_data_elev_shift.dat"
)

d1_obj = modem.Data()
d1_obj.read_data_file(inv01_dfn)

d2_obj = modem.Data()
d2_obj.read_data_file(inv02_dfn)

d1_obj.data_array["rel_east"][:] = d2_obj.data_array["rel_east"][:]
d1_obj.data_array["rel_north"][:] = d2_obj.data_array["rel_north"][:]
d1_obj.data_array["elev"][:] = d2_obj.data_array["elev"][:]

d1_obj.write_data_file(
    save_path=d2_obj.save_path,
    fn_basename="mont_data_elev_edit.dat",
    compute_error=False,
    fill=False,
)
