# -*- coding: utf-8 -*-
"""
Created on Wed Dec  9 20:09:13 2020

:author: Jared Peacock

:license: MIT

"""

from mtpy.modeling.modem import Data

dfn = r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GreatBasin\modem_inv\inv_02\gb_modem_data_z03_t02_edits.dat"

new_fns = [r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GreatBasin\modem_inv\inv_02\edi_files\AVG055.edi",
           r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GreatBasin\modem_inv\inv_02\edi_files\AVG056.edi",
           r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GreatBasin\modem_inv\inv_02\edi_files\SP05.edi",
           r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GreatBasin\modem_inv\inv_02\edi_files\USArray.CAM02.2010.edi",
           r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GreatBasin\modem_inv\inv_02\edi_files\USArray.CAM06.2010.edi"]

d = Data()
d.read_data_file(dfn)
d.error_type_z = "eigen_floor"
d.error_value_z = .03
d.error_type_tipper = "abs_floor"
d.error_value_tipper = 0.02
d.model_epsg = 32611
d.data_array, d.mt_dict = d.add_station(fn=new_fns)

d.write_data_file(fn_basename="gb_modem_data_z03_t02_add.dat",
                  compute_error=False,
                  fill=False)