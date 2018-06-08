# -*- coding: utf-8 -*-
"""
Created on Fri Jun 08 11:08:52 2018

@author: jrpeacock
"""

import urllib2 as url
import xml.etree.ElementTree as ET


lat = 45.765893
lon = -118.648693

nm_url = r"https://nationalmap.gov/epqs/pqs.php?x={0:.3f}&y={1:.3f}&units=Meters&output=xml".format(lon, lat)

response = url.urlopen(nm_url)

# read the xml file
info = ET.ElementTree(ET.fromstring(response.read()))
info = info.getroot()
for elev in info.iter('Elevation'):
    nm_elev = float(elev.text)
    
print nm_elev


