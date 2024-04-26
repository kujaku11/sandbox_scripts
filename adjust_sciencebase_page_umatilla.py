# -*- coding: utf-8 -*-
"""
Adjust Sciencebase layout.

.. note:: Run in a Python shell to avoid having your password echoed on screen

Created on Wed Oct 24 11:35:51 2018

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
from pathlib import Path
import json
import sciencebasepy as sb


# =============================================================================
# Parameters
# =============================================================================
page_id = "60dcb4c5d34e3a6dca21f73d"
username = "jpeacock@usgs.gov"


page_summary = (
    "This data set consists of 19 wideband magnetotelluric (MT) and 23 "
    "transient electromagnetic (TEM) soundings collected by the U.S. "
    "Geological Survey in June 2020 as part of the Umatilla Indian Reservation "
    "Geothermal Resources Assessment: Phase 2 project. Each MT station had 4 "
    "components, 2 orthogonal magnetic induction coils and 2 horizontal "
    "orthogonal electric dipoles. Data were collected for an average of 18 "
    "hours on a repeating schedule of alternating sampling rates of 256 "
    "samples/second for 5 hours and 50 minutes and 4096 samples/second for "
    "10 minutes. The schedules were set such that each station was recording"
    " the same schedule to allow for remote reference processing. Data were "
    "processed with a bounded-influence robust remote reference processing "
    "scheme (BIRRP v5.2.1, Chave and Thomson, 2004). Data quality were "
    "generally poor due to episodic spikes in the electromagnetic fields "
    "likely caused by the power grid. TEM data were collected in 100 x 100 m "
    "loops or 40 x 40 m loops along 4 profiles in areas of interest for "
    "geothermal potential. Files included in this publication include "
    "measured electric- and magnetic-field time series for MT data, MT "
    "transfer functions, TEM soundings, and 1-D resistivity models from the "
    "TEM soundings."
)
title = "Magnetotelluric and TEM Data from the Umatilla Indian Reservation Geothermal Resources Assessment: Phase 2, 2020"

# =============================================================================
# login and get child ids
# =============================================================================
sb_session = sb.SbSession("beta")
sb_session.get_token()
fn = input("input filename: ")
with open(fn, "r") as fid:
    tk = json.load(fid)["science_base_token"]
sb_session.add_token(tk)

child_ids = sb_session.get_child_ids(page_id)
# =============================================================================
# Change json
# =============================================================================
for child_id in child_ids:
    try:
        child_json = sb_session.get_item(child_id)
    except:
        print(f"---> skipping child id {child_id}".format())
        continue

    ### adjust citation
    station = child_json["title"][-6:].strip()

    ### adjust summary
    child_json["title"] = f"{title}: MT station {station}"

    print("{'='*7} {station} {'='*7}")
    child_json["citation"] = (
        "Peacock, J. R. and Pepin, J. D., 2024, Magnetotelluric and TEM Data "
        "from the Umatilla Indian Reservation Geothermal Resources Assessment: "
        f"Phase 2, 2020: Station {station}: U.S. Geological Survey data release, "
        "https://doi.org/10.5066/P9DQJTL9."
    )

    #### UPDATE CHILD ITEM
    sb_session.update_item(child_json)
