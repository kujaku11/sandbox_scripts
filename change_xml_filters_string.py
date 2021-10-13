# -*- coding: utf-8 -*-
"""
Created on Fri Oct  8 15:21:32 2021

@author: jpeacock
"""

from pathlib import Path

xml_path = Path(r"c:\Users\jpeacock\OneDrive - DOI\mt\mt_array_xmls")
save_path = Path(r"c:\Users\jpeacock\OneDrive - DOI\mt\mt_array_xmls\new")

hx_filter_str = "nT to counts, magnetic field 3 pole Butterworth low-pass, Hx time offset"
hy_filter_str = "nT to counts, magnetic field 3 pole Butterworth low-pass, Hy time offset"
hz_filter_str = "nT to counts, magnetic field 3 pole Butterworth low-pass, Hz time offset"
e_filter_str = ("mV/km to V/m, V/m to V, V to counts, electric field 1 pole "
        "Butterworth high-pass, electric field 5 pole Butterworth low-pass, "
            "electric time offset")

new_hx = "magnetic_nanotesla_to_counts, magnetic_butterworth_low_pass, hx_time_offset"
new_hy = "magnetic_nanotesla_to_counts, magnetic_butterworth_low_pass, hy_time_offset"
new_hz = "magnetic_nanotesla_to_counts, magnetic_butterworth_low_pass, hz_time_offset"

new_e = ("electric_si_units, dipole_length, "
         "electric_analog_to_digital, electric_butterworth_high_pass, "
         "electric_butterworth_low_pass, electric_time_offset")

for fn in xml_path.glob("*.xml"):
    if fn.stem.count(".") > 2:
        comp = fn.stem.split(".")[3].lower()
        with open(fn, mode="r") as fid:
            fn_str = fid.read()
            if "hx" in comp:
                fn_str = fn_str.replace(hx_filter_str, new_hx)
            elif "hy" in comp:
                fn_str = fn_str.replace(hy_filter_str, new_hy)
            elif "hz" in comp:
                fn_str = fn_str.replace(hz_filter_str, new_hz)
            elif comp in ["ex", "ey"]:
                fn_str = fn_str.replace(e_filter_str, new_e)
        with open(save_path.joinpath(fn.name), "w") as fid:
            fid.write(fn_str)
            
    
                
        
    