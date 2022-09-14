# -*- coding: utf-8 -*-
"""
Created on Wed Jan 12 17:20:09 2022

@author: jpeacock
"""

from pathlib import Path
import numpy as np
import pandas as pd

from mtpy.core.mt import MT


def make_fn_df(df_fn, original_path, new_path):
    original = Path(original_path)
    phase_01 = Path(new_path)

    fn_list = []
    for f1 in original.glob("*.edi"):
        m1 = MT(f1)
        m1.read_tf_file()
        for f2 in phase_01.glob("*.edi"):
            m2 = MT(f2)
            m2.read_tf_file()
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
        r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\2022_EDI_files_birrp_processed\GeographicNorth\SS"
    ),
):

    save_dir = Path(save_dir)
    if not save_dir.exists():
        save_dir.mkdir()

    df = pd.read_csv(df_fn)

    ss_rows = []
    for row in df.itertuples():
        m1 = MT(row.original)
        m1.read_tf_file()
        m2 = MT(row.phase_01)
        m2.read_tf_file()

        z1, t1 = m1.interpolate(m2.frequency, bounds_error=False)

        sx = np.median(z1.res_xy[:nf] / m2.Z.res_xy[:nf])
        sy = np.median(z1.res_yx[:nf] / m2.Z.res_yx[:nf])

        print(f"station: {m1.station} - {m2.station}: sx={sx}, sy={sy}\n")

        m2.Z = m2.remove_static_shift(1.0 / sx, 1.0 / sy)
        tf = m2.write_tf_file(save_dir=save_dir)
        ss_rows.append({f"{df.columns[-1]}_ss": tf.fn, "sx": sx, "sy": sy})

    ss_df = pd.DataFrame(ss_rows)
    df = df.join(ss_df)
    df.to_csv(df_fn)


# =============================================================================
#
# =============================================================================

df_fn = r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\phase_02_filenames.csv"

make_fn_df(
    df_fn,
    r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\2021_EDI_files_birrp_processed\GeographicNorth",
    r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\2022_EDI_files_birrp_processed\GeographicNorth",
)

remove_static_shift(
    df_fn,
    save_dir=r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\2022_EDI_files_birrp_processed\GeographicNorth\SS",
)
