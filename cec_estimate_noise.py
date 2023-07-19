# -*- coding: utf-8 -*-
"""

Created on Sun May  7 20:51:10 2023

:author: Jared Peacock

:license: MIT

"""


from pathlib import Path
from mth5 import read_file
from scipy import signal
import xarray as xr


gz_path = Path(r"c:\MT\GZ2023")

fn_list = list(gz_path.rglob("*011017_256_EX.Z3D"))

ex1 = read_file(fn_list[0])
ex1.ts = ex1.data_array.sps_filters.low(30)
ex1.ts = signal.detrend(ex1.ts)

for fn in fn_list[1:]:
    print(f"--> reading {fn.name}")
    ex2 = read_file(fn)
    ex2.start = ex1.start
    ex2.ts = ex2.data_array.sps_filters.low(30)
    ex2.ts = signal.detrend(ex2.ts)
    ex1.data_array = xr.merge(
        [ex1.data_array, ex2.data_array], join="exact", compat="override"
    ).to_array(name="ex")
ex1.plot()
ex1.plot_spectra()
