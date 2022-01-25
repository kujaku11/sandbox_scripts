# -*- coding: utf-8 -*-
"""
Created on Wed Nov 10 14:31:28 2021

@author: jpeacock
"""
from pathlib import Path
from mtpy.modeling.modem import Data, Model

mfn_base = Path(r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\modem_inv\repeat_01\gz_base_sm.rho")
mfn_repeat_01 = Path(r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\modem_inv\repeat_01\gz_z05_c03_061.rho")

m_base = Model()
m_base.read_model_file(mfn_base)

m_repeat = Model()
m_repeat.read_model_file(mfn_repeat_01)

# m_base.res_model = m_base.res_model / m_repeat.res_model
m_base.res_model = m_repeat.res_model - m_base.res_model

m_base.write_vtk_file(vtk_fn_basename="cec_repeat_01_difference",
                      label="resistivity")
