# -*- coding: utf-8 -*-
"""
Created on Tue Jul 26 10:32:32 2022

@author: jpeacock
"""

# =============================================================================
# Imports
# =============================================================================
from pathlib import Path
import sciencebasepy as sb
import getpass
from archive.utils import sb_tools
from archive.mt_xml import MTSBXML


# =============================================================================
# Parameters
# =============================================================================
page_id = "60dcb385d34e3a6dca21e4b9"
username = "jpeacock@usgs.gov"
password = getpass.getpass()
xml_path = Path(r"c:\Users\jpeacock\Documents\scec_xml_files\edited")

# =============================================================================
# login and get child ids
# =============================================================================
sb_session = sb.SbSession()
sb_session.login(username, password)

# =============================================================================
# Upload xml files
# =============================================================================

for xml_fn in list(xml_path.glob("*.xml")):
    print(f"===== {xml_fn.stem} =====")
    child_id = sb_tools.sb_locate_child_item(sb_session, xml_fn.stem, page_id)

    # x = MTSBXML()
    # x.read(xml_fn)
    child_item = sb_session.get_item(child_id)
    # child_item["summary"] = str(x.metadata.idinfo.descript.abstract.text)
    # child_item["body"] = str(x.metadata.idinfo.descript.abstract.text)

    child_item["contacts"] = [
        {
            "name": "Jared Peacock",
            "type": "Point of Contact",
            "contactType": "person",
            "email": "jpeacock@usgs.gov",
            "jobTitle": "Research Geophysicist",
            "organization": {"displayText": "U.S. Geological Survey"},
            "primaryLocation": {
                "officePhone": "650-329-2833",
                "faxPhone": "303-236-1425",
                "streetAddress": {},
                "mailAddress": {
                    "line1": "PO Box 158",
                    "city": "Moffett Field",
                    "state": "CA",
                    "zip": "94035",
                    "country": "USA",
                },
            },
        },
        {
            "name": "U.S. Geological Survey",
            "type": "Point of Contact",
            "contactType": "organization",
            "email": "jpeacock@usgs.gov",
            "jobTitle": "Research Geophysicist",
            "organization": {},
            "primaryLocation": {
                "officePhone": "650-329-2833",
                "faxPhone": "303-236-1425",
                "streetAddress": {},
                "mailAddress": {
                    "line1": "PO Box 158",
                    "city": "Moffett Field",
                    "state": "CA",
                    "zip": "94035",
                    "country": "USA",
                },
            },
        },
        {
            "name": "Jared Peacock and Pieter-Ewald Share-MacParland",
            "type": "Originator",
            "organization": {},
            "primaryLocation": {"streetAddress": {}, "mailAddress": {}},
        },
        {
            "name": "Jared Peacock",
            "type": "Metadata Contact",
            "contactType": "person",
            "email": "jpeacock@usgs.gov",
            "jobTitle": "Research Geophysicist",
            "organization": {"displayText": "U.S. Geological Survey"},
            "primaryLocation": {
                "officePhone": "650-329-2833",
                "faxPhone": "303-236-1425",
                "streetAddress": {},
                "mailAddress": {
                    "line1": "PO Box 158",
                    "city": "Moffett Field",
                    "state": "CA",
                    "zip": "94035",
                    "country": "USA",
                },
            },
        },
        {
            "name": "U.S. Geological Survey",
            "type": "Metadata Contact",
            "contactType": "organization",
            "email": "jpeacock@usgs.gov",
            "jobTitle": "Research Geophysicist",
            "organization": {},
            "primaryLocation": {
                "officePhone": "650-329-2833",
                "faxPhone": "303-236-1425",
                "streetAddress": {},
                "mailAddress": {
                    "line1": "PO Box 158",
                    "city": "Moffett Field",
                    "state": "CA",
                    "zip": "94035",
                    "country": "USA",
                },
            },
        },
        {
            "name": "GS ScienceBase",
            "type": "Distributor",
            "contactType": "person",
            "email": "sciencebase@usgs.gov",
            "organization": {"displayText": "U.S. Geological Survey"},
            "primaryLocation": {
                "officePhone": "1-888-275-8747",
                "streetAddress": {},
                "mailAddress": {
                    "line1": "Denver Federal Center, Building 810, Mail Stop 302",
                    "city": "Denver",
                    "state": "CO",
                    "zip": "80225",
                    "country": "United States",
                },
            },
        },
        {
            "name": "U.S. Geological Survey",
            "type": "Distributor",
            "contactType": "organization",
            "email": "sciencebase@usgs.gov",
            "organization": {},
            "primaryLocation": {
                "officePhone": "1-888-275-8747",
                "streetAddress": {},
                "mailAddress": {
                    "line1": "Denver Federal Center, Building 810, Mail Stop 302",
                    "city": "Denver",
                    "state": "CO",
                    "zip": "80225",
                    "country": "United States",
                },
            },
        },
        {
            "name": "Geology, Minerals, Energy, and Geophysics Science Center",
            "oldPartyId": 17468,
            "type": "Data Owner",
            "contactType": "organization",
            "onlineResource": "https://www.usgs.gov/centers/gmeg",
            "active": True,
            "aliases": [
                '{"name":"GNEGSC"}',
                '{"name":"GEOLOGY & GEOPHYSICS SC"}',
            ],
            "fbmsCodes": ["GGWSZT0000"],
            "logoUrl": "http://my.usgs.gov/static-cache/images/dataOwner/v1/logosMed/USGSLogo.gif",
            "smallLogoUrl": "http://my.usgs.gov/static-cache/images/dataOwner/v1/logosSmall/USGSLogo.gif",
            "organization": {},
            "primaryLocation": {
                "name": "USGS Menlo Park Campus - Bldg. 2 [WMB]",
                "building": "Bldg. 2",
                "buildingCode": "WMB",
                "streetAddress": {
                    "line1": "345 Middlefield Road",
                    "city": "Menlo Park",
                    "state": "CA",
                    "zip": "94025-3561",
                    "country": "USA",
                },
                "mailAddress": {
                    "line1": "345 Middlefield Road",
                    "city": "Menlo Park",
                    "state": "CA",
                    "zip": "94025",
                    "country": "USA",
                },
            },
        },
        {
            "name": "Southern California Earthquake Center",
            "type": "Funding Agency",
            "onlineResource": "https://www.scec.org/",
            "organization": {},
            "primaryLocation": {"streetAddress": {}, "mailAddress": {}},
        },
        {
            "name": "Institute of Geophysics and Planetary Physics, University of California, San Diego",
            "type": "Cooperator/Partner",
            "onlineResource": "https://igpp.ucsd.edu/about",
            "organization": {},
            "primaryLocation": {"streetAddress": {}, "mailAddress": {}},
        },
    ]

    new_child_json = sb_session.update_item(child_item)
    print("    updated contacts")

    # sb_session.delete_file(xml_fn.name, child_item)
    # print(f"    deleting {xml_fn.name}")
    # sb_session.upload_file_to_item(
    #     child_item, xml_fn.as_posix(), scrape_file=True
    # )
    # print(f"    uploaded {xml_fn.name}")


sb_session.logout()

# # =============================================================================
# # Download all the xml files
# # =============================================================================
# children = sb_session.get_child_ids(page_id)

# download_list = []
# for child_id in children:
#     child = sb_session.get_item(child_id)
#     file_names = [{"name": c["name"], "url": c["url"]} for c in child["files"]]
#     for ftype in [".xml"]:
#         try:
#             fn_dict = [fn for fn in file_names if fn["name"].endswith(ftype)][
#                 0
#             ]
#         except IndexError:
#             print(f"Could not find {ftype} file in {child['title']} ")
#             continue

#         sb_session.download_file(
#             fn_dict["url"],
#             fn_dict["name"],
#             destination=r"c:\Users\jpeacock\Documents\scec_xml_files",
#         )
#         print(f"--> downloaded {fn_dict['name']}")

#         download_list.append(fn_dict["name"])
