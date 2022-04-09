# -*- coding: utf-8 -*-
"""
This script will rotate principle axis back to geographic coordinates.

Created on Wed Jan 26 11:07:21 2022

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
from pathlib import Path
from mtpy.core.mt import MT

# =============================================================================

edi_path = Path(r"c:\Users\jpeacock\OneDrive - DOI\mt\principle_axis")

for edi_filename in edi_path.glob("*.edi"):
    m = MT(edi_filename)
    m.Z.rotate(m.Z.rotation_angle)
    m.Tipper.rotate(m.Tipper.rotation_angle)

    p = m.plot_mt_response(plot_num=2)
    p.save_plot(
        edi_path.joinpath(f"{m.station}_geographic.png").as_posix(), fig_dpi=300
    )

    m.write_mt_file(fn_basename=f"{m.station}_geographic.edi")
