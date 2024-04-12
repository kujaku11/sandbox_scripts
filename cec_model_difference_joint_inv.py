# -*- coding: utf-8 -*-
"""
Created on Wed Dec  6 10:18:23 2023

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
from pathlib import Path
import pandas as pd
import numpy as np

# =============================================================================

m21 = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\modem_inv\gz_2021_joint_resistivity_casp_nad27_zone_2_ft.xyz"
)
m23 = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\modem_inv\gz_2023_joint_resistivity_casp_nad27_zone_2_ft.xyz"
)

df21 = pd.read_csv(
    m21, header=24, names=["north", "east", "depth", "resistivity"]
)
df23 = pd.read_csv(
    m23, header=24, names=["north", "east", "depth", "resistivity"]
)


df21c = df21[["north", "east", "depth"]].copy()
df23c = df23[["north", "east", "depth"]].copy()

df21c["conductivity"] = 1.0 / (10**df21.resistivity)
df23c["conductivity"] = 1.0 / (10**df23.resistivity)

df_diff = df21[["north", "east", "depth"]].copy()
df_diff["conductivity"] = (
    (df23c.conductivity - df21c.conductivity) / df21c.conductivity * 100
)
df_diff.conductivity[df_diff.conductivity == np.inf] = 0

df_diff.to_csv(
    m21.parent.joinpath("mt_2023_vs_2021_joint_percent.xyz"), index=False
)

df21c.to_csv(
    m21.parent.joinpath(
        "gz_2021_joint_resistivity_casp_nad27_zone_2_ft_s_per_m.xyz"
    ),
    index=False,
)
df23c.to_csv(
    m21.parent.joinpath(
        "gz_2023_joint_resistivity_casp_nad27_zone_2_ft_s_per_m.xyz"
    ),
    index=False,
)
