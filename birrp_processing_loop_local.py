# -*- coding: utf-8 -*-
"""
Created on Mon Sep 26 12:32:29 2016

@author: jpeacock
"""

import os
import shutil
import mtpy.usgs.zen_processing as zp
from cStringIO import StringIO
import sys


class Capturing(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        sys.stdout = self._stdout


# ==============================================================================
# local parameters
# ==============================================================================
coil_calibration_path = r"/mnt/hgfs/MTData/Ant_calibrations/rsp_cal"
birrp_path = r"/home/jpeacock/Documents/birrp/birrp52_4pcs16e9pts"
local_path = r"/mnt/hgfs/MTData/MB"
copy_edi_path = os.path.join(local_path, "EDI_Files_birrp")

if not os.path.isdir(copy_edi_path):
    os.mkdir(copy_edi_path)

# ==============================================================================
# Need to copy from the external hard drive first, cause paths are too long
# ==============================================================================


def process_station(
    station,
    rr_station,
    birrp_path,
    local_path,
    copy_edi_path,
    coil_calibration_path,
    fn_copy=True,
):
    """
    process station 
    """
    station_path = os.path.join(local_path, station)
    if rr_station is not None:
        rr_station_path = os.path.join(local_path, rr_station)
    else:
        rr_station_path = None
    # ==============================================================================
    # Process data
    # ==============================================================================
    b_param_dict = {
        "c2threshb": 0.45,
        "c2threshe": 0.45,
        "c2thresh1": 0.45,
        "ainuin": 0.9995,
        "ainlin": 0.0001,
        "nar": 5,
    }

    zp_obj = zp.Z3D_to_edi(station_dir=station_path, rr_station_dir=rr_station_path)
    zp_obj.birrp_exe = birrp_path
    zp_obj.coil_cal_path = coil_calibration_path
    plot_obj, comb_edi_fn = zp_obj.process_data(
        df_list=[4096, 256, 16],
        notch_dict={4096: {}, 256: None, 16: None},
        max_blocks=3,
        sr_dict={4096: (1000.0, 25), 256: (24.999, 0.126), 16: (0.125, 0.0001)},
        birrp_param_dict=b_param_dict,
    )

    cp_edi_fn = os.path.join(copy_edi_path, station + ".edi")
    shutil.copy(comb_edi_fn, cp_edi_fn)
    print "--> Copied {0} to {1}".format(comb_edi_fn, cp_edi_fn)
    return plot_obj, comb_edi_fn


# ==============================================================================
# run the loop
# ==============================================================================
# station_list = [('ms21', 'ms11'),
#                ('ms11', 'ms21'),
#                ('ms71', 'ms32'),
#                ('ms32', 'ms71'),
#                ('ms22', 'ms71'),
#                ('ms83', 'ms71'),
#                ('ms70', 'ms31'),
#                ('ms31', 'ms70'),
#                ('ms33', 'ms44'),
#                ('ms44', 'ms33'),
#                ('ms78', 'ms44'),
#                ('ms80', 'ms44'),
#                ('ms85', 'ms86'),
#                ('ms12', 'ms86')]
station_list = [
    ("mb28", "mb02"),
    ("mb02", "mb28"),
    ("mb69", "mb81"),
    ("mb81", "mb69"),
    ("mb85", "mb69"),
    ("mb89", "mb69"),
    ("mb27", "mb56"),
    ("mb56", "mb27"),
    ("mb57", "mb27"),
    ("mb47", "mb48"),
    ("mb48", "mb47"),
    ("mb59", "mb47"),
    ("mb83", "mb49"),
    ("mb49", "mb83"),
    ("mb61", "mb83"),
    ("mb82", "mb45"),
    ("mb45", "mb82"),
    ("mb32", "mb82"),
    ("mb26", "mb44"),
    ("mb44", "mb26"),
    ("mb13", "mb44"),
    ("mb15", "mb33"),
    ("mb33", "mb15"),
    ("mb14", "mb15"),
    ("mb53", "mb43"),
    ("mb43", "mb53"),
    ("mb42", "mb53"),
    ("mb86", "mb99"),
    ("mb99", "mb86"),
]

edi_fn_list = []

for s_tuple in station_list:
    with Capturing() as output:
        try:
            p_obj, edi_fn = process_station(
                s_tuple[0],
                s_tuple[1],
                birrp_path,
                local_path,
                copy_edi_path,
                coil_calibration_path,
                fn_copy=True,
            )
            p_obj.fig.savefig(os.path.join(local_path, s_tuple[0] + ".png"), dpi=1200)
            p_obj.fig.clear()
            edi_fn_list.append(edi_fn)
        except:
            print "Could not process {0} because {1}".format(
                s_tuple[0], sys.exc_info()[0]
            )

        finally:
            print "!!!Processing Failed!!!"
    with open(os.path.join(local_path, s_tuple[0] + ".log"), "w") as fid:
        fid.write("\n".join(output))
