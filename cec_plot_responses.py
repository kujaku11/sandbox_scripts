# -*- coding: utf-8 -*-
"""
Created on Wed Jan 12 17:20:09 2022

@author: jpeacock
"""

from pathlib import Path
import numpy as np
import pandas as pd

from mtpy.imaging import mtplot
from mtpy.core.mt import MT

df_fn = r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\phase_01_filenames.csv"


def make_fn_df(df_fn):
    original = Path(
        r"c:\Users\jpeacock\OneDrive - DOI\Geysers\EDI_Files_birrp\Edited\Geographic"
    )
    phase_01 = Path(
        r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\EDI_files_birrp_processed\Geographic\Edited"
    )

    fn_list = []
    for f1 in original.glob("*.edi"):
        m1 = MT(f1)
        for f2 in phase_01.glob("*.edi"):
            m2 = MT(f2)
            if np.isclose(m1.latitude, m2.latitude, 0.0001) and np.isclose(
                m1.longitude, m2.longitude, 0.0001
            ):
                fn_list.append({"original": f1, "phase_01": f2})
                print(m1.station, m2.station)
                break
    df = pd.DataFrame(fn_list)
    df.to_csv(df_fn, index=False)


def remove_static_shift(
    df_fn,
    nf=22,
    save_dir=Path(
        r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\EDI_files_birrp_processed\Geographic\Edited\SS"
    ),
):
    df = pd.read_csv(df_fn)

    for row in df.itertuples():
        m1 = MT(row.original)
        m2 = MT(row.phase_01)

        m1.Z, m1.Tipper = m1.interpolate(m2.frequencies, bounds_error=False)

        sx = np.median(m1.Z.res_xy[:nf] / m2.Z.res_xy[:nf])
        sy = np.median(m1.Z.res_yx[:nf] / m2.Z.res_yx[:nf])

        print(f"station: {m1.station} - {m2.station}: sx={sx}, sy={sy}")

        m2.Z = m2.remove_static_shift(1.0 / sx, 1.0 / sy)
        m2.write_mt_file(save_dir=save_dir)


remove_static_shift(df_fn)
