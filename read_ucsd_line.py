# -*- coding: utf-8 -*-
"""
Created on Mon Nov 30 15:43:54 2020

:author: Jared Peacock

:license: MIT

"""

from pathlib import Path
import pandas as pd
from mtpy.core.mt import MT

epath = Path(r"c:\Users\jpeacock\Documents\milipitas")
spath = Path(r"c:\Users\jpeacock\Documents\milipitas\new_edis")
loc_fn = Path(r"c:\Users\jpeacock\Documents\milipitas\latlon_NAD83.txt")

df = pd.read_csv(loc_fn)

for fn in epath.glob("*.edi"):
    m = MT(fn)
    m.station = f"{m.station}_{fn.stem}"
    l = df[df.Station == fn.stem]
    m.latitude = l.Latitude.values[0]
    m.longitude = l.Longitude.values[0]
    m.elevation = l.Elevation.values[0]
    m.write_mt_file(save_dir=spath)

    p = m.plot_mt_response(plot_num=2)
    p.save_plot(spath.joinpath(f"{m.station}.png").as_posix(), fig_dpi=300)
