# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 08:56:50 2019

@author: jpeacock
"""

from mtpy.modeling import modem

mfn = r"c:\Users\jpeacock\Documents\Geysers\gz_sm50_topo_ocean_shifted.rho"
dfn = r"c:\Users\jpeacock\Documents\Geysers\gz_modem_data_r50_z05_topo_edit.dat"

d_obj = modem.Data()
d_obj.read_data_file(dfn)

m_obj = modem.Model()
m_obj.read_model_file(mfn)

d_obj.project_stations_on_topography(m_obj)
d_obj.write_vtk_station_file()
