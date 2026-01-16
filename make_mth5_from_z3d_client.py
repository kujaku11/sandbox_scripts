# -*- coding: utf-8 -*-
"""
Created on Tue Nov 19 14:45:04 2024

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
from pathlib import Path
from mth5.clients import MakeMTH5

# =============================================================================
survey_stem = "cl"

survey_path = Path(r"c:\Users\jpeacock\OneDrive - DOI\MTData\CL2025")
mth5_path = survey_path.joinpath("mth5")
mth5_path.mkdir(exist_ok=True, parents=True)

for folder in list(survey_path.iterdir())[1:]:
    if folder.is_dir() and folder.name.startswith(survey_stem):
        print(folder.name)

        MakeMTH5.from_zen(
            folder,
            save_path=mth5_path.joinpath(f"{folder.name}.h5"),
            calibration_path=r"c:\Users\jpeacock\OneDrive - DOI\MTData\antenna_20190411.cal",
            survey_id="cl2025",
            station_stem=survey_stem,
        )
