# -*- coding: utf-8 -*-
"""
Created on Thu Apr 20 10:04:20 2023

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
import numpy as np
from mtpy.modeling.modem import Data

# =============================================================================

d = Data()
 = d.read_data_file(
    r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GreatBasin\modem_inv\gb_02\gb_modem_data_z10_t05.dat"
)


## check for zeros in model error
for comp in ["zxx", "zxy", "zyx", "zyy", "tzx", "tzy"]:
    find_zeros = np.where(df.dataframe[f"{comp}_model_error"] == 0)[0]
    if find_zeros.shape[0] > 0:
        print(f"Found errors with 0 value in {comp} {len(find_zeros)} times.")
        if "z" in comp:
            error_percent = d.z_model_error.error_value
        elif "t" in comp:
            error_percent = d.t_model_error.error_value
        df.dataframe[f"{comp}_model_error"].iloc[list(find_zeros)] = (
            abs(df.dataframe[f"{comp}"].iloc[list(find_zeros)]) * error_percent
        )

## check for really small errors
tol = 0.02
for comp in ["zxx", "zxy", "zyx", "zyy", "tzx", "tzy"]:
    find_small = np.where(
        df.dataframe[f"{comp}_model_error"] / abs(df.dataframe[comp]) < tol
    )[0]
    if find_small.shape[0] > 0:
        print(
            f"Found errors with values less than {tol} in {comp} {len(find_small)} times."
        )
        if "z" in comp:
            error_percent = d.z_model_error.error_value
        elif "t" in comp:
            error_percent = d.t_model_error.error_value
        df.dataframe[f"{comp}_model_error"].iloc[list(find_zeros)] = (
            abs(df.dataframe[f"{comp}"].iloc[list(find_zeros)]) * error_percent
        )

d.dataframe = df.dataframe
d.write_data_file(
    save_path=d.data_filename.parent,
    fn_basename=f"{d.data_filename.stem}_02.dat",
)
