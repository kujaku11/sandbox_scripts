# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
# =============================================================================
# imports
# =============================================================================

from pathlib import Path
from mtpy import MTData, MTCollection

# =============================================================================
# with MTCollection as mc:
#     mc.open_collection(
#         r"c:\Users\jpeacock\OneDrive - DOI\ClearLake\modem_inv\magma_tests\cl_magma_tests.h5"
#     )
#     md = mc.to_mt_data()


data_fn = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\ClearLake\modem_inv\inv_05_topo\cl_modem_data_z03_t02_tec_11.dat"
)

magma_path = Path(r"c:\Users\jpeacock\OneDrive - DOI\ClearLake\modem_inv\magma_tests")
resp_fn = magma_path.joinpath("cl_z03_t02_c02_040_11.dat")
# resp_fn = Path(
#     r"c:\Users\jpeacock\OneDrive - DOI\ClearLake\modem_inv\inv_05_topo\cl_z03_t02_c02_040.dat"
# )
# resp_fn_02 = Path(
#     r"c:\Users\jpeacock\OneDrive - DOI\ClearLake\modem_inv\inv_05_topo\cl_z03_t02_c02x2_028.dat"
# )

# resp_fn_03 = Path(
#     r"c:\Users\jpeacock\OneDrive - DOI\ClearLake\modem_inv\inv_05_topo\clvf_z03_t02_c02_smavg_042.dat"
# )

# build data
d = MTData()
# d.from_modem(data_fn, survey="data")
d.from_modem(resp_fn, survey="inv_z03_t02_c02_040_11")
# d.from_modem(resp_fn_02, survey="inv_z03_t02_c02x2_028")
# d.from_modem(resp_fn_03, survey="inv_z03_t02_c02_smavg_042")
# fn_list = list(magma_path.glob("cl_gpc_*.dat")) + list(magma_path.glob("cl_deep*.dat"))
#  fn_list = list(magma_path.glob("cl_gpc_depth_test*.dat"))  # + list(
#    magma_path.glob("cl_test_li_deep_*.dat")
# )
# for fn in fn_list:
#     survey_id = "_".join(fn.stem.split("_")[-2:])
#     d.from_modem(fn, survey=survey_id)

with MTCollection() as mc:
    mc.open_collection(magma_path.joinpath("cl_magma_tests_02.h5"))
    mc.from_mt_data(d)

# station = "cl326"

# pr = d.plot_mt_response(
#     [
#         f"data.{station}",
#         f"inv_model.{station}",
#         f"17km_30ohmm.{station}",
#         f"17km_20ohmm.{station}",
#         f"17km_10ohmm.{station}",
#         f"17km_3ohmm.{station}",
#         f"60km_30ohmm.{station}",
#         f"60km_10ohmm.{station}",
#         f"60km_3ohmm.{station}",
#     ],
#     plot_style="compare",
#     fig_num=2,
# )
