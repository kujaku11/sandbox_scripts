# -*- coding: utf-8 -*-
"""
Created on Mon Jul 24 12:50:14 2017

@author: jpeacock
"""
from pathlib import Path
import numpy as np
from mtpy.core import mt
from mtpy.core import z
import os
from mtpy.imaging import mtplot

edi_01 = Path(r"c:\Users\jpeacock\OneDrive - DOI\EDI_FILES\MNP124.edi")
edi_02 = Path(r"c:\Users\jpeacock\OneDrive - DOI\EDI_FILES\USMTArray.CAW11.2019.edi")

c_edi_fn = edi_01.parent.joinpath("{0}_c.edi".format(edi_01.stem))
if c_edi_fn.exists():
    os.remove(c_edi_fn)

fc_dict = {0: (1000, 0.003), 1: (0.0029, 0.000001)}

ss_dict = {0: (1, 1), 1: (0.3, 0.5)}

data_arr = np.zeros(
    150,
    dtype=[
        ("freq", np.float),
        ("z", (np.complex, (2, 2))),
        ("z_err", (np.float, (2, 2))),
        ("tipper", (np.complex, (2, 2))),
        ("tipper_err", (np.float, (2, 2))),
    ],
)

count = 0
for ii, edi_fn in enumerate([edi_01, edi_02]):
    mt_obj = mt.MT(edi_fn)

    f_index = np.where(
        (mt_obj.Z.freq >= fc_dict[ii][1]) & (mt_obj.Z.freq <= fc_dict[ii][0])
    )

    z_ss = mt_obj.remove_static_shift(ss_x=ss_dict[ii][0], ss_y=ss_dict[ii][1])
    # if ii == 1:
    #     z_ss.z[:, 0, :] *= -(1 + 1.7j)

    data_arr["freq"][count : count + len(f_index[0])] = z_ss.freq[f_index]
    data_arr["z"][count : count + len(f_index[0])] = z_ss.z[f_index]
    data_arr["z_err"][count : count + len(f_index[0])] = z_ss.z_err[f_index]
    if mt_obj.Tipper.tipper is not None:
        data_arr["tipper"][count : count + len(f_index[0])] = mt_obj.Tipper.tipper[
            f_index
        ]
        data_arr["tipper_err"][
            count : count + len(f_index[0])
        ] = mt_obj.Tipper.tipper_err[f_index]

    count += len(f_index[0])


# now replace
data_arr = data_arr[np.nonzero(data_arr["freq"])]
sort_index = np.argsort(data_arr["freq"])

# check to see if the sorted indexes are descending or ascending,
# make sure that frequency is descending
if data_arr["freq"][0] > data_arr["freq"][1]:
    sort_index = sort_index[::-1]

data_arr = data_arr[sort_index]
new_z = z.Z(data_arr["z"], data_arr["z_err"], data_arr["freq"])

# check for all zeros in tipper, meaning there is only
# one unique value
if np.unique(data_arr["tipper"]).size > 1:
    new_t = z.Tipper(data_arr["tipper"], data_arr["tipper_err"], data_arr["freq"])

else:
    new_t = z.Tipper()

mt_obj = mt.MT(edi_01)
mt_obj.Z = new_z
mt_obj.Tipper = new_t
n_edi_fn = mt_obj.write_mt_file(fn_basename=c_edi_fn.name)

ptm = mtplot.plot_multiple_mt_responses(
    fn_list=[edi_01, edi_02, n_edi_fn], plot_style="compare", plot_tipper="yr",
)
