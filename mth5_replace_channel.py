from mth5.mth5 import MTH5
import numpy as np


import pandas as pd
import numpy as np

time_fluff_dict = {1: 12 * 3600, 256: 4 * 3600, 4096: 2 * 60}


def compute_overlap(row_01, row_02):
    start_diff = abs(row_01.start.timestamp() - row_02.start.timestamp())
    end_diff = abs(row_01.end.timestamp() - row_02.end.timestamp())

    if (
        start_diff < time_fluff_dict[row_01.sample_rate]
        and end_diff < time_fluff_dict[row_01.sample_rate]
    ):
        return True
    else:
        return False


def find_matching_row(row_01, df_02):
    for row_02 in df_02.itertuples():
        if compute_overlap(row_01, row_02):
            print(
                f"Found match for {row_01.station}{row_01.run}{row_01.start} "
                f"and {row_02.station}{row_02.run}{row_02.start}"
            )
            return row_02
    return None


# with MTH5() as m1:
#     m1 = m1.open_mth5(
#         r"c:\Users\jpeacock\OneDrive - DOI\MTData\SAGE2026\mth5\sg2606.h5"
#     )
#     ch_summary_06 = m1.channel_summary.to_dataframe()
#     ch_summary_06 = ch_summary_06.loc[ch_summary_06["component"] == "hy"]
#     with MTH5() as m2:
#         m2 = m2.open_mth5(
#             r"c:\Users\jpeacock\OneDrive - DOI\MTData\SAGE2026\mth5\sg2607.h5"
#         )
#         ch_summary_07 = m2.channel_summary.to_dataframe()
#         ch_summary_07 = ch_summary_07.loc[ch_summary_07["component"] == "hy"]

#         for channel in ch_summary_07.itertuples():
#             ch_07 = m2.from_reference(channel.hdf5_reference)
#             ch_07_ts = ch_07.to_channel_ts()
#             sr_06 = ch_summary_06.loc[
#                 (ch_summary_06["sample_rate"] == channel.sample_rate)
#             ]
#             row_06 = find_matching_row(channel, sr_06)
#             if row_06 is not None:
#                 ch_06 = m1.from_reference(row_06.hdf5_reference).to_channel_ts()
#                 ch_07.ts = ch_06.get_slice(ch_07.start, ch_07.end)
#                 ch_07.from_channel_ts(ch_07.ts)

# with MTH5() as m1:
#     m1 = m1.open_mth5(
#         r"c:\Users\jpeacock\OneDrive - DOI\MTData\SAGE2026\mth5\sg2606.h5"
#     )
#     sg = m1.get_survey("SAGE2026")
#     f1 = sg.filters_group.to_filter_object("ant4_4314_response")
#     with MTH5() as m2:
#         m2 = m2.open_mth5(
#             r"c:\Users\jpeacock\OneDrive - DOI\MTData\SAGE2026\mth5\sg2607.h5"
#         )

#         sg_07 = m2.get_survey("SAGE2026")
#         sg_07.filters_group.add_filter(f1)
#         print(f"Added filter {f1.name}")

with MTH5() as m2:
    m2 = m2.open_mth5(
        r"c:\Users\jpeacock\OneDrive - DOI\MTData\SAGE2026\mth5\sg2607.h5"
    )

    ch_summary_07 = m2.channel_summary.to_dataframe()
    ch_hy = ch_summary_07.loc[ch_summary_07["component"] == "hy"]
    for row in ch_hy.itertuples():
        ch = m2.from_reference(row.hdf5_reference)
        ch.metadata.filters = [ch.metadata.filters[-1], ch.metadata.filters[-2]]
        ch.write_metadata()
