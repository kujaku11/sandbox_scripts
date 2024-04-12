# -*- coding: utf-8 -*-
"""
Created on Tue Sep  5 11:45:09 2023

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
from pathlib import Path
from mtpy import MT

# =============================================================================

xml_path = Path(r"c:\Users\jpeacock\Downloads\SPUD_bundle_2023-09-05T18.41.27")
save_path = xml_path.parent.joinpath("brod_nv")
if not save_path.exists():
    save_path.mkdir()

for xml_fn in xml_path.rglob("*.xml"):
    mt_obj = MT()
    mt_obj.read(xml_fn)
    mt_obj.station = f"brod_{mt_obj.station}"

    mt_obj.write(fn=save_path.joinpath(f"{mt_obj.station}.edi"))

    # p1 = mt_obj.plot_mt_response(plot_num=2)
    # p1.save_plot(save_path.joinpath(f"brod_{mt_obj.station}.png"), fig_dpi=300)
