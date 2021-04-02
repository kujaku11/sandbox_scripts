# -*- coding: utf-8 -*-
"""
Created on Thu Aug 27 13:17:03 2020

:author: Jared Peacock

:license: MIT

"""

from pathlib import Path
from mtpy.utils import shapefiles

edi_dir = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GabbsValley\EDI_Files_birrp\Edited\Interpolated"
)

edi_list = list(edi_dir.glob("*.edi"))

# ptm = shapefiles.PTShapeFile(edi_list,
#                              save_path=r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GabbsValley\EDI_Files_birrp\Edited\Interpolated\pt")
# ptm.write_shape_files()

tip = shapefiles.TipperShapeFile(
    edi_list,
    save_path=r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GabbsValley\EDI_Files_birrp\Edited\Interpolated\pt",
)
tip.write_imag_shape_files()
tip.write_real_shape_files()
