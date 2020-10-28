# -*- coding: utf-8 -*-
"""
Created on Thu Mar 01 12:19:36 2018

@author: jpeacock
"""

import mtpy.modeling.modem as modem

dfn = r"c:\Users\jpeacock\Documents\iMush\modem_inv\shz_inv_02\shz_modem_data_ef04_tip03.dat"

d = modem.Data()
d.read_data_file(dfn)

imush = ["name,lat,lon"]
pfa = ["name,lat,lon"]
gh = ["name,lat,lon"]

for s_arr in d.station_locations.station_locations:
    line = "{0},{1:.5f},{2:.5f}".format(s_arr[0], s_arr[1], s_arr[2])
    if s_arr[0][0] in ["0", "1", "2"]:
        imush.append(line)
    elif s_arr[0][0] in ["5", "6"]:
        gh.append(line)
    else:
        pfa.append(line)

for survey, name in zip([imush, pfa, gh], ["imush", "pfa", "gh"]):
    fn = "c:\Users\jpeacock\Documents\iMush\{0}_station_locations.txt".format(name)
    lines = ["name,lat,lon"]
    with open(fn, "w") as fid:
        fid.write("\n".join(survey))
