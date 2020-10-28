# -*- coding: utf-8 -*-
"""
Created on Tue Mar 11 11:05:58 2014

@author: jpeacock-pr
"""

import os
import numpy as np
import mtpy.core.edi as mtedi
import mtpy.core.z as mtz
import mtpy.utils.latlongutmconversion as utmll

data_file = r"C:\Users\jpeacock-pr\Documents\MonoBasin\LV_Wannamaker\LVMTdat.txt"
loc_file = r"c:\Users\jpeacock-pr\Documents\MonoBasin\LV_Wannamaker\LV-LOC.txt"
well_loc = (-118.908611, 37.679722)

save_path = r"c:\Users\jpeacock-pr\Documents\MonoBasin\LV_Wannamaker"

well_zone, well_east, well_north = utmll.LLtoUTM(23, well_loc[1], well_loc[0])
dipole_len = 100
# ==============================================================================
# read location file
# ==============================================================================
loc_fid = file(loc_file, "r")

loc_lines = loc_fid.readlines()

ns = int(loc_lines[0].strip())

locations = np.zeros(ns, dtype=[("name", "|S10"), ("lat", np.float), ("lon", np.float)])
loc_dict = {}
for ii, line in enumerate(loc_lines[1 : ns + 1]):
    line_list = line.strip().split(",")
    name = line_list[0]
    north = float(line_list[1]) * 1000
    east = float(line_list[2]) * 1000

    lat, lon = utmll.UTMtoLL(23, well_north + north, well_east + east, well_zone)
    locations[ii]["name"] = name
    locations[ii]["lat"] = lat
    locations[ii]["lon"] = lon

    loc_dict[name] = (lat, lon)

# ==============================================================================
# read data file
# ==============================================================================
data_fid = file(data_file, "r")

ns = int(data_fid.readline())

data_list = []

for jj, line in enumerate(data_fid.readlines()):
    line_list = line.strip().split()
    if len(line_list) == 1:
        line_test = line_list[0].split(",")
        if len(line_test) == 1:
            name = "LV{0:02}".format(int(line_list[0]))
            f_index = None
            nf = 1
        else:
            nf = int(line_test[0])
            pcount = 0
            f_index = 0
            frequency = np.zeros(nf, dtype=np.float)
            res = np.zeros((nf, 2, 2), dtype=np.float)
            phase = np.zeros((nf, 2, 2), dtype=np.float)
            res_err = np.zeros_like(res)
            phase_err = np.zeros_like(phase)
            tipper = np.zeros((nf, 1, 2), dtype=np.complex)
            tipper_err = np.zeros_like(tipper, dtype=np.float)
    elif len(line_list) == 5:
        res[f_index, 0, 0] = float(line_list[0])
        res_err[f_index, 0, 0] = 10 ** float(line_list[1])
        res[f_index, 0, 1] = float(line_list[2])
        res_err[f_index, 0, 1] = 10 ** float(line_list[3])
        frequency[f_index] = float(line_list[4])
        pcount = 1
    elif len(line_list) == 4:
        if pcount == 1:
            res[f_index, 1, 0] = float(line_list[0])
            res_err[f_index, 1, 0] = 10 ** float(line_list[1])
            res[f_index, 1, 1] = float(line_list[2])
            res_err[f_index, 1, 1] = 10 ** float(line_list[3])
            pcount += 1
        elif pcount == 2:
            phase[f_index, 0, 0] = float(line_list[0])
            phase_err[f_index, 0, 0] = float(line_list[1])
            phase[f_index, 0, 1] = float(line_list[2])
            phase_err[f_index, 0, 1] = float(line_list[3])
            pcount += 1
        elif pcount == 3:
            phase[f_index, 1, 0] = float(line_list[0])
            phase_err[f_index, 1, 0] = float(line_list[1])
            phase[f_index, 1, 1] = float(line_list[2])
            phase_err[f_index, 1, 1] = float(line_list[3])
            pcount += 1
    elif len(line_list) == 6:
        tipper[f_index, 0, 0] = float(line_list[0]) + float(line_list[1]) * 1j
        tipper_err[f_index, 0, 0] = float(line_list[2])
        tipper[f_index, 0, 1] = float(line_list[3]) + float(line_list[4]) * 1j
        tipper_err[f_index, 0, 1] = float(line_list[5])
        f_index += 1

    if f_index == nf:
        data_list.append(
            {
                "name": name,
                "res": res,
                "phase": phase,
                "res_err": res_err,
                "phase_err": phase,
                "tipper": tipper,
                "tipper_err": tipper_err,
            }
        )
        print "Station = {0}, no. freq = {1}".format(name, nf)

        # write edi file
        data_edi = mtedi.Edi()
        data_z = mtz.Z()
        data_z.freq = frequency
        data_z.set_res_phase(res, phase, reserr_array=res_err, phaseerr_array=phase_err)

        data_T = mtz.Tipper(tipper_array=tipper, tippererr_array=tipper_err)
        data_T.freq = frequency

        data_edi.Z = data_z
        data_edi.Tipper = data_T

        # ---------------HEADER----------------------------------------------
        data_edi.head = dict(
            [
                ("dataid", name),
                ("acqby", "P. E. Wannamaker"),
                ("fileby", "P.E. Wannamaker"),
                ("acqdate", "Nov. 1986"),
                ("loc", "Long Valley, CA"),
                ("lat", loc_dict[name][0]),
                ("lon", loc_dict[name][1]),
                ("elev", 2200),
            ]
        )

        # ----------------INFO------------------------------------------------
        data_edi.info_dict = dict(
            [
                ("max lines", 1000),
                ("equipment", "see Young et al., 1988"),
                ("processing", "see Stodt, 1983"),
            ]
        )
        # ----------------DEFINE MEASUREMENT----------------------------------
        data_edi.definemeas = dict(
            [
                ("maxchan", 5),
                ("maxrun", 999),
                ("maxmeas", 99999),
                ("units", "m"),
                ("reftype", "cartesian"),
                ("reflat", loc_dict[name][0]),
                ("reflon", loc_dict[name][1]),
                ("refelev", 2200),
            ]
        )

        # -----------------HMEAS EMEAS-----------------------------------------
        hmeas_emeas = []
        hmeas_emeas.append(["HMEAS", "ID=1", "CHTYPE=HX", "X=0", "Y=0", "AZM=340", ""])
        hmeas_emeas.append(["HMEAS", "ID=2", "CHTYPE=HY", "X=0", "Y=0", "AZM=70", ""])
        hmeas_emeas.append(["HMEAS", "ID=3", "CHTYPE=HZ", "X=0", "Y=0", "AZM=0", ""])
        hmeas_emeas.append(
            ["EMEAS", "ID=4", "CHTYPE=EX", "X=0", "Y=0", "X2=100", "Y2=0"]
        )
        hmeas_emeas.append(
            ["EMEAS", "ID=5", "CHTYPE=EY", "X=0", "Y=0", "X2=0", "Y2=100"]
        )
        hmeas_emeas.append(["HMEAS", "ID=6", "CHTYPE=RHX", "X=0", "Y=0", "AZM=340", ""])
        hmeas_emeas.append(["HMEAS", "ID=7", "CHTYPE=RHY", "X=0", "Y=0", "AZM=70", ""])

        hmstring_list = []
        for hm in hmeas_emeas:
            hmstring_list.append(" ".join(hm))
        data_edi.hmeas_emeas = hmstring_list
        # ------------MTSECT------------------------------------------------
        data_edi.mtsect = dict(
            [
                ("sectid", name),
                ("nfreq", frequency.shape[0]),
                ("HX", 1),
                ("HY", 2),
                ("HZ", 3),
                ("EX", 4),
                ("EY", 5),
            ]
        )

        # ------------ZROT--------------------------------------------------
        data_edi.zrot = np.zeros(frequency.shape[0])
        data_edi.zrot[:] = 340

        # ------------FREQ--------------------------------------------------
        data_edi.freq = frequency

        # --> write .edi file
        edi_fn = data_edi.writefile(os.path.join(save_path, "{0}.edi".format(name)))
