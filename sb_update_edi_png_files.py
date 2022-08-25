# -*- coding: utf-8 -*-
"""
Created on Wed Jul 27 11:12:29 2022

@author: jpeacock
"""

# =============================================================================
# Imports
# =============================================================================
from pathlib import Path
import sciencebasepy as sb
import getpass


# =============================================================================
# Parameters
# =============================================================================
page_id = "60dcb385d34e3a6dca21e4b9"
username = "jpeacock@usgs.gov"
password = getpass.getpass()
edi_path = Path(r"c:\Users\jpeacock\OneDrive - DOI\SCEC_2019\final_edi_new")
png_path = Path(r"c:\Users\jpeacock\OneDrive - DOI\SCEC_2019\final_png_new")

# =============================================================================
# login and get child ids
# =============================================================================
sb_session = sb.SbSession()
sb_session.login(username, password)

child_ids = sb_session.get_child_ids(page_id)

for child_id in child_ids:
    try:
        child_item = sb_session.get_item(child_id)
    except:
        print("---> skipping child id {0}".format(child_id))
        continue

    station = child_item["title"].lower().split(": station ")[-1]
    print(f"===== {station} =====")
    edi_fn = edi_path.joinpath(f"{station}.edi")
    # png_fn = png_path.joinpath(f"{station}.png")

    # sb_session.delete_file(edi_fn.name, child_item)
    # print(f"    deleted EDI file: {edi_fn.name}")
    sb_session.upload_file_to_item(
        child_item, edi_fn.as_posix(), scrape_file=False
    )
    print(f"    Uploaded EDI file: {edi_fn.name}")

    # sb_session.delete_file(png_fn.name, child_item)
    # print(f"    deleted PNG file: {png_fn.name}")
    # sb_session.upload_file_to_item(
    #     child_item, png_fn.as_posix(), scrape_file=False
    # )
    # print(f"    Uploaded PNG file: {png_fn.name}")


sb_session.logout()
