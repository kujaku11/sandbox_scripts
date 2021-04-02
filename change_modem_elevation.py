# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 16:31:44 2020

@author: jpeacock
"""

from mtpy.modeling import modem
import numpy as np

dfn = r"c:\Users\jpeacock\OneDrive - DOI\LV\Inversions\MonoLake\inv_03\ml_modem_data_z03_t02_topo_edit.dat"
mfn = r"c:\Users\jpeacock\OneDrive - DOI\LV\Inversions\MonoLake\inv_03\ml_modem_sm02_topo_lake.rho"

z_change = [
    ("MB173", 1),
    ("MB156", 1),
    ("MB090", 1),
    ("MB115", 1),
    ("MB143", 1),
    ("cay204", 1),
    ("MB109", 1),
    ("MB113", 1),
    ("MB069", 1),
    ("MB071", 1),
    ("MB114", 1),
    ("MB036", 1),
    ("MB038", 1),
    ("MB041", 2),
    ("MB122", 4),
    ("MB054", 1),
    ("MB509", 1),
    ("MB130", 3),
    ("MB129", 3),
    ("MB503", 2),
    ("A6", 2),
    ("MB530", 1),
    ("MB170", -1),
    ("MB074", -1),
    ("MB126", -1),
    ("MB059", -1),
    ("MB521", -2),
    ("MB522", -3),
    ("MB523", -2),
    ("MB527", -1),
    ("B4.5", -2),
    ("MB524", -1),
    ("B4", -2),
    ("E3", -1),
    ("D3", -1),
]

d_obj = modem.Data()
d_obj.read_data_file(dfn)

m_obj = modem.Model()
m_obj.read_model_file(mfn)

for zz in z_change:
    s_index = np.where(d_obj.data_array["station"] == zz[0])[0][0]
    s_arr = d_obj.data_array[s_index]
    z_index = np.where(m_obj.grid_z == (s_arr["rel_elev"] - 0.001))[0][0]
    new_elev = m_obj.grid_z[z_index - zz[1]]
    s_arr["rel_elev"] = m_obj.grid_z[z_index + zz[1]] + 0.001

    print(
        "{0}: z_0={1:.2f}, z1={2:.2f}".format(
            s_arr["station"], m_obj.grid_z[z_index], s_arr["rel_elev"]
        )
    )
