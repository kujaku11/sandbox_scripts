# -*- coding: utf-8 -*-
"""
Check database statistics for a science base archive

Created on Tue Oct 30 18:58:29 2018

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
import sciencebasepy as sb
import getpass
import pandas as pd

# =============================================================================
# Parameters
# =============================================================================
page_url = "5ad77f06e4b0e2c2dd25e798"
username = "jpeacock@usgs.gov"
password = getpass.getpass()

# =============================================================================
# login and get child ids
# =============================================================================
sb_session = sb.SbSession()
sb_session.login(username, password)

child_ids = sb_session.get_child_ids(page_url)
# =============================================================================
# Change json
# =============================================================================
data = []

for child_id in child_ids:
    try:
        child_json = sb_session.get_item(child_id)
    except:
        print("---> skipping child id {0}".format(child_id))
        continue

    # get station name from title
    station = child_json["title"].split()[1]

    # get the total size of all the files
    total_file_size = sum([fn_dict["size"] for fn_dict in child_json["files"]])

    # get the number of files
    n_files = len(child_json["files"])

    # check to make child has all the files
    fn_list = [fn_dict["name"] for fn_dict in child_json["files"]]
    has_edi = False
    has_png = False
    has_xml = False
    has_zips = False
    for fn in fn_list:
        if fn.endswith("xml"):
            has_xml = True
        elif fn.endswith("edi"):
            has_edi = True
        elif fn.endswith("png"):
            has_png = True
        elif fn.endswith("zip"):
            has_zips = True
        else:
            pass

    data.append(
        (station, n_files, total_file_size, has_xml, has_edi, has_png, has_zips)
    )

# =============================================================================
# make data frame and write to csv
# =============================================================================
df = pd.DataFrame(
    data, columns=("station", "n_files", "size", "xml", "edi", "png", "zips")
)

df.to_csv(r"c:\Users\jpeacock\Documents\iMush\sb_stats.csv", index=False)
