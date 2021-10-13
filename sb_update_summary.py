# -*- coding: utf-8 -*-
"""
Created on Thu Sep  2 09:07:30 2021

@author: jpeacock
"""
import os
import sciencebasepy as sb
import time

page_id = "60d39cc1d34e12a1b009c64b"
username = "jpeacock@usgs.gov"


# initialize a session
session = sb.SbSession()

# login to session, note if you run this in a console your password will
# be visible, otherwise run from a command line > python sciencebase_upload.py
session.loginc(username)

# need to wait a few seconds to connect otherwise bad things happen
time.sleep(5)

count = 0
for child in session.get_child_ids(page_id):
    page_dict = session.get_item(child)
    station = page_dict["title"].split()[-1].strip()
    summary = (
        "This data set consists of 59 wideband magnetotelluric (MT) stations "
        "collected by the U.S. Geological Survey in July and August of 2020 as "
        "part of a 1-year project funded by the Energy Resources Program of the "
        "U.S. Geological Survey to demonstrate full crustal control on geothermal "
        "systems in the Great Basin. Each station had 5 components, 3 orthogonal"
        " magnetic induction coils and 2 horizontal orthogonal electric dipoles. "
        " Data were collected for an average of 18 hours on a repeating schedule "
        "of alternating sampling rates of 256 samples/second for 7 hours and 50 "
        "minutes and 4096 samples/second for 10 minutes.  The schedules were set "
        "such that each station was recording the same schedule to allow for "
        "remote reference processing.  Data were processed with a bounded-influence"
        " robust remote reference processing scheme (BIRRP v5.2.1, Chave and "
        "Thomson, 2004).  Data quality is good for periods of 0.007 - 2048 with "
        "some noise in the higher periods and less robust estimates at the "
        "longer periods.   Files included in this publication include measured "
        f"electric- and magnetic-field time series ({station}.h5) as well as "
        "estimated impedance and vertical-magnetic field transfer functions "
        f"({station}.edi).  An image of the MT response is supplied ({station}.png) "
        "where the impedance tensor is plotted on the to two panels, the "
        "induction vectors in the middle panel (up is geographic North), "
        "and the phase tensor in the bottom panel (up is geographic North).  "
        "The real induction vectors point towards strong conductors.  "
        "Phase tensor ellipses align in the direction of electrical current "
        "flow and warmer color represents the subsurface becoming more conductive "
        "and cooler colors more resistive. All plots are on the same period "
        "scale [10E-3, 10E+4] seconds."
    )
    page_dict["summary"] = summary
    page_dict["body"] = summary
    session.update_item(page_dict)
    print(f"--> {count}: Updated {station}")
    count += 1
