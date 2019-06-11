# -*- coding: utf-8 -*-
"""
Created on Fri Apr 26 16:44:42 2019

@author: jpeacock
"""
import numpy as np
from mtpy.modeling import modem
from scipy import interpolate

fn = r"c:\Users\jpeacock\Documents\Geysers\modem_inv\inv04\gz_rm50_z03_c05_107.rho"

def glover(sigma_1, phi_1, m_1, sigma_2, phi_2, m_2, 
           sigma_3=None, phi_3=None, m_3=None):
    sigma_eff = sigma_1 * phi_1**m_1 + sigma_2 * phi_2**m_2
    if sigma_3 is not None:
        sigma_eff += sigma_3 * phi_3**m_3

    return sigma_eff

phi_3 = .04
m_3 = 3
sigma_3 = 100
saturation = np.linspace(phi_3, 1, 25)
s = 1./glover(1./70, 1-saturation, 1,
              1./1000, saturation, 2, 
              sigma_3, phi_3, m_3)

s_interp = interpolate.interp1d(s, saturation, kind='slinear',
                                bounds_error=False, 
                                fill_value=np.NAN,
                                assume_sorted=False)

m = modem.Model()
m.read_model_file(fn)

res = s_interp(m.res_model.copy().flatten()).reshape(m.res_model.shape)

m.res_model = res.copy()
m.write_model_file(model_fn_basename='gz_saturation.rho')
m.write_vtk_file(vtk_fn_basename='gz_saturation')


