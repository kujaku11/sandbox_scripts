#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  4 12:14:53 2022

@author: peacock
"""

from pathlib import Path
from archive.mt_xml import MTSBXML

archive_dir = Path(r"c:\Users\jpeacock\Documents\scec_xml_files")

for xml_fn in list(archive_dir.glob("*.xml")):

    x = MTSBXML()
    x.read(xml_fn)

    # # # update title
    # # x.metadata.idinfo.citation.citeinfo.title.text += f": Station {station}"

    # update description
    x.metadata.idinfo.descript.abstract.text = (
        x.metadata.idinfo.descript.abstract.text.replace(
            "was lead",
            "was led",
        )
    )

    x.metadata.idinfo.descript.abstract.text = x.metadata.idinfo.descript.abstract.text.replace(
        "EMTF",
        "the robust remote reference code EMTF (Egbert, 1997; DOI: https://doi.org/10.1111/j.1365-246X.1997.tb05663.x)",
    )
    x.metadata.idinfo.descript.abstract.text = (
        x.metadata.idinfo.descript.abstract.text.replace(
            "sps", "samples per second"
        )
    )
    # text = xml_fn.read_text().split("\n")
    # with open(xml_fn, "w") as fid:
    #     fid.write("\n".join(text[0:115]+["     </keywords>"] + text[115:]))

    # change vertical deforintion
    x.metadata.spref.vertdef.altsys.altdatum.text = (
        "North American Vertical Datum of 1988 (NAVD 88)"
    )

    x.validate()
    x.save(xml_fn.parent.joinpath("edited", xml_fn.name))
