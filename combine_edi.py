# -*- coding: utf-8 -*-
"""
Created on Thu Oct 19 15:28:51 2017

@author: jpeacock-pr
"""
# import shutil
from pathlib import Path
import mtpy.usgs.zen_processing as zp
import mtpy.imaging.plotnresponses as pmr
import mtpy.imaging.plotresponse as pr


station = "cv172"
station_path = Path(r"/mnt/hgfs/MT_Data/GB2022/{0}".format(station))
copy_path = Path(r"/mnt/hgfs/MT_Data/GB2022/EDI_files_birrp")

# station_path = Path(r"c:\MT\MT_Data\GZ2021\{0}".format(station))

s_dict = {"4096": 0, "256": 0, "4": 0}

edi_fn_list = []
for sr, index in s_dict.items():
    if index == 0:
        fn = f"{station}.edi"
    else:
        fn = f"{station}_{index}.edi"
    edi_fn_list.append(station_path.joinpath("TS", "BF", sr, fn))
p1 = pmr.PlotMultipleResponses(fn_list=edi_fn_list, plot_style="compare")

k = zp.Z3D2EDI()
k.station_ts_dir = station_path.joinpath("TS")
nedi = k.combine_edi_files(
    edi_fn_list, sr_dict={4096: (1000.0, 50), 256: (49.9, 0.01), 4: (0.01, 0.00001)}
)

p2 = pr.PlotResponse(fn=nedi, plot_tipper="yri", fig_num=3)

# copy = input("copy file?")
# if copy in ["y", "true", True]:
#     shutil.copy(nedi, copy_path.joinpath(f"{station}.edi"))
#     print("copied {station} to edi path")
