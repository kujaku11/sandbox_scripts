# -*- coding: utf-8 -*-
"""
Created on Thu Jul 11 15:29:40 2024

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
from pathlib import Path
from mth5.io.zen import Z3DCollection
from loguru import logger

# =============================================================================


folder = Path(r"C:\Users\jpeacock\OneDrive - DOI\MTData")

survey_dict = {
    # "BM2022": {"survey": "BM2022"}
    # "BV2023": {"survey": "BV2023"},
    # "CL2021": {"survey": "CL2021"},
    # "Camas": {"survey": "CM2018"},
    # "GabbsValley": {"survey": "GV2017"},
    # "Geysers": {"survey": "GZ2017"},
    # "GraniteSprings": {"survey": "GS2017"},
    # "GV2020": {"survey": "GV2022"},
    # "GZ2021": {"survey": "GZ2021"},
    # "GZ2022": {"survey": "GZ2022"},
    # "GZ2023": {"survey": "GZ2023"},
    # "LD2024": {"survey": "LD2024"},
    # "LV": {"survey": "LV2016"},
    # "MB": {"survey": "MB2016"},
    # "MB_2015": {"survey": "MB2015"},
    # "MNP2019": {"survey": "MNP2019"},
    # "MountainHome": {"survey": "MH2018"},
    # "MountainPass": {"survey": "MP2015"},
    # "MP": {"survey": "MP2017"},
    # "MSH": {"survey": "MSHN2016"},
    # "MSHS": {"survey": "MSHS2016"},
    # "MusicValley": {"survey": "MV2017"},
    # "SanPabloBay": {"survey": "SPB2015"},
    # "UM": {"survey": "UMTIR2020"},
    # "Umatilla": {"survey": "UMTIR2017"},
    "CM2025": {"survey": "ColumbusMarsh2025"},
}

for key, sdict in survey_dict.items():
    try:
        survey_path = folder.joinpath(key)
        zc = Z3DCollection(file_path=survey_path)
        df = zc.to_dataframe(sample_rates=[256, 1024, 4096])
        sdf = df.groupby("station", as_index=False).first()
        sdf.survey = sdict["survey"]

        # summarize into something useful
        for station in sdf.station.unique():
            sdf.loc[sdf.station == station, "start"] = df[
                df.station == station
            ].start.min()
            sdf.loc[sdf.station == station, "end"] = df[
                df.station == station
            ].end.max()
            sdf.loc[sdf.station == station, "latitude"] = df[
                df.station == station
            ].latitude.mean()
            sdf.loc[sdf.station == station, "longitude"] = df[
                df.station == station
            ].longitude.mean()
            sdf.loc[sdf.station == station, "elevation"] = df[
                df.station == station
            ].elevation.mean()

            sdf.loc[sdf.station == station, "dipole_ex"] = df[
                (df.station == station) & (df.component == "ex")
            ].dipole.mean()
            sdf.loc[sdf.station == station, "dipole_ey"] = df[
                (df.station == station) & (df.component == "ey")
            ].dipole.mean()

            sdf.loc[sdf.station == station, "hx"] = (
                df[(df.station == station) & (df.component == "hx")]
                .coil_number.astype(int)
                .mean()
            )
            sdf.loc[sdf.station == station, "hy"] = (
                df[(df.station == station) & (df.component == "hy")]
                .coil_number.astype(int)
                .mean()
            )
            sdf.loc[sdf.station == station, "hz"] = (
                df[(df.station == station) & (df.component == "hz")]
                .coil_number.astype(int)
                .mean()
            )

            sdf.loc[sdf.station == station, "components"] = " ".join(
                sorted(list(df[df.station == station].component.unique()))
            )

        sdf[
            [
                "station",
                "survey",
                "start",
                "end",
                "latitude",
                "longitude",
                "elevation",
                "instrument_id",
                "components",
                "dipole_ex",
                "dipole_ey",
                "hx",
                "hy",
                "hz",
            ]
        ].to_csv(survey_path.joinpath("survey_summary.csv"), index=False)
        print(f"FINISHED {key}")

    except Exception as error:
        print(f"ERROR: {key}\n{error}")
        logger.exception(error)
