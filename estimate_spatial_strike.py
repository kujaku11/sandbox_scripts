# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 10:22:42 2020

:author: Jared Peacock

:license: MIT

"""
# =============================================================================
# Imports
# =============================================================================
import pandas as pd

from mtpy.modeling import modem

# =============================================================================
#
# =============================================================================
dfn = r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GabbsValley\modem_inv\st_topo_inv_02\st_modem_data_z05_t02_topo.dat"

d_obj = modem.Data()
d_obj.read_data_file(dfn)

strike_list = []
for k, m in d_obj.mt_dict.items():
    for st, st_err, sk, sk_err, per, tip in zip(
        m.pt.azimuth,
        m.pt.azimuth_err,
        m.pt.skew,
        m.pt.skew_err,
        m.pt.freq,
        m.Tipper.angle_real,
    ):
        tip = tip + 90
        if tip > 90:
            tip -= 180
        line = {
            "station": m.station,
            "latitude": m.latitude,
            "longitude": m.longitude,
            "period": 1.0 / per,
            "strike": st,
            "t_strike": tip,
            "skew": sk,
            "strike_err": st_err,
            "skew_err": sk_err,
        }
        strike_list.append(line)

df = pd.DataFrame(strike_list)

df.to_csv(
    r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GabbsValley\gv_mt_strike_and_skew.csv",
    index=False,
)
