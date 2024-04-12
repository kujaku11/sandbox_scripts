# -*- coding: utf-8 -*-
"""
Created on Wed Nov 10 14:31:28 2021

@author: jpeacock
"""
from pathlib import Path
import numpy as np
from mtpy.modeling import StructuredGrid3D


model_dict = {
    "2021": {
        "fn": Path(
            r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\modem_inv\larger_grid_2021\gz_2021_z03_c02_048.rho"
        ),
    },
    "2022": {
        "fn": Path(
            r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\modem_inv\larger_grid_2022\gz_2022_z03_c02_NLCG_132.rho"
        ),
    },
    "2023": {
        "fn": Path(
            r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\modem_inv\larger_grid_2023\gz_2023_z03_t02_c02_107.rho"
        ),
    },
}

compare_list = [["2021", "2022"], ["2021", "2023"], ["2022", "2023"]]

for m1, m2 in compare_list:
    m_base = StructuredGrid3D()
    m_base.from_modem(model_dict[m1]["fn"])

    m_repeat = StructuredGrid3D()
    m_repeat.from_modem(model_dict[m2]["fn"])

    # m_base.res_model = m_base.res_model / m_repeat.res_model
    # m_base.res_model = (
    #     (m_repeat.res_model - m_base.res_model) / m_base.res_model
    # ) * 100
    m_base.res_model = m_repeat.res_model - m_base.res_model

    m_base.to_vtk(
        vtk_save_path=r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\modem_inv",
        vtk_fn_basename=f"cec_repeat_{m1}_vs_{m2}_diff_abs",
        label="resistivity",
    )
