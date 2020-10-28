# -*- coding: utf-8 -*-
"""
Convert spectra data to impedance

Created on Fri Aug  3 09:31:58 2018

@author: jpeacock
"""

import os
import mtpy.core.mt as mt

# import mtpy.usgs.usgs_archive as archive
import urllib2 as url
import xml.etree.ElementTree as ET

# =============================================================================
#
# =============================================================================
def get_nm_elev(lat, lon):
    """
    Get national map elevation for a given lat and lon.

    Queries the national map website for the elevation value.

    :param lat: latitude in decimal degrees
    :type lat: float

    :param lon: longitude in decimal degrees
    :type lon: float

    :return: elevation (meters)
    :rtype: float

    :Example: ::

        >>> import mtpy.usgs.usgs_archive as archive
        >>> archive.get_nm_elev(35.467, -115.3355)
        >>> 809.12

    .. note:: Needs an internet connection to work.

    """
    nm_url = r"https://nationalmap.gov/epqs/pqs.php?x={0:.5f}&y={1:.5f}&units=Meters&output=xml"

    # call the url and get the response
    try:
        response = url.urlopen(nm_url.format(lon, lat))
    except url.HTTPError:
        print("GET_ELEVATION_ERROR: Could not connect to internet")
        return -666

    # read the xml response and convert to a float
    info = ET.ElementTree(ET.fromstring(response.read()))
    info = info.getroot()
    for elev in info.iter("Elevation"):
        nm_elev = float(elev.text)
    return nm_elev


# =============================================================================
# Inputs
# =============================================================================
edi_path = r"c:\Users\jpeacock\Documents\MonoBasin\BR_EDI_Files"
location_csv = (
    r"c:\Users\jpeacock\Documents\MonoBasin\BR_EDI_Files\Mono Basin WGS84.txt"
)

# =============================================================================
# make parameters
# =============================================================================
sv_path = os.path.join(edi_path, "Impedance")
if not os.path.exists(sv_path):
    os.mkdir(sv_path)

edi_list = [
    os.path.join(edi_path, edi) for edi in os.listdir(edi_path) if edi.endswith(".edi")
]

s_dict = {}
with open(location_csv, "r") as fid:
    lines = fid.readlines()

ab_dict = {"A": 100, "B": 200, "C": 300, "D": 400, "E": 500, "F": 600, "G": 700}

for line in lines[2:]:
    line_list = line.split()
    if len(line_list) != 3:
        continue
    line_list = [l.strip() for l in line_list]
    s_label = line_list[0][0]
    s_number = int(line_list[0][1:].replace(".", ""))
    if s_number < 10:
        s_number *= 10
    s = "{0}".format(ab_dict[s_label] + s_number)
    s_dict[s] = {
        "station": line_list[0],
        "lat": float(line_list[1]),
        "lon": float(line_list[2]),
    }

# =============================================================================
# Loop over edi files and make impedance
# =============================================================================
for edi_fn in edi_list:
    st_dict = s_dict[os.path.basename(edi_fn)[0:-4]]
    mt_obj = mt.MT(edi_fn)
    mt_obj.station = st_dict["station"]
    mt_obj.lat = st_dict["lat"]
    mt_obj.lon = st_dict["lon"]
    mt_obj.elev = get_nm_elev(st_dict["lat"], st_dict["lon"])
    mt_obj.write_mt_file(save_dir=sv_path)
    # p = mt_obj.plot_mt_response(plot_num=2)
    # p.save_plot(os.path.join(sv_path, mt_obj.station+'.png'), fig_dpi=600)
