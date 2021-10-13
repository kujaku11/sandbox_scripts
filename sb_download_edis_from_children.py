# -*- coding: utf-8 -*-
"""
Created on Tue Sep  7 11:11:14 2021

@author: jpeacock
"""

from pathlib import Path
import sciencebasepy as sb

# BRod 2003 Northeast Nevada
page_id = "59c54adbe4b017cf313d5850"

# BRod 2007 North Wells Nevada
page_id = "59ba6d0ce4b091459a563b34"
save_path = r"c:\Users\jpeacock\OneDrive - DOI\EDI_FILES"

session = sb.SbSession()

children = session.get_child_ids(page_id)

for child_id in children:
    child = session.get_item(child_id)
    file_names = [{"name": c["name"], "url": c["url"]} for c in child["files"]]
    try:
        edi_dict = [fn for fn in file_names if fn["name"].endswith(".edi")][0]
    except IndexError:
        print(f"Could not find EDI file in {child['title']} ")
        continue

    session.download_file(edi_dict["url"], edi_dict["name"], destination=save_path)
    print(f"--> downloaded {edi_dict['name']}")
