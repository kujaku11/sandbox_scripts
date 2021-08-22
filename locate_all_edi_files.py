# -*- coding: utf-8 -*-
"""
Created on Fri Apr 19 14:39:53 2019

@author: jpeacock
"""

import os
import pandas as pd
import glob

edi_dirs = ["c:\Users\jpeacock", "d:\Peacock\MTData"]
fn_df_csv = os.path.join(edi_dirs[0], "all_edi_files.csv")
if not os.path.exists(fn_df_csv):
    fn_df = pd.DataFrame()
    for edi_dir in edi_dirs:
        for root, dirs, fn_list in os.walk(edi_dir):
            for fn in fn_list:
                if glob.fnmatch.fnmatch(fn, "*.edi"):
                    fn_dict = {}
                    fn_dict["station"] = [fn[:-4].lower().split("_")[0]]
                    fn_dict["fn_path"] = [os.path.join(root, fn)]
                    fn_dict["fn_date"] = [os.path.getmtime(fn_dict["fn_path"][0])]
                    fn_df = fn_df.append(pd.DataFrame(fn_dict))
                    fn_df.reset_index()

    fn_df.to_csv(fn_df_csv, index=False)
### need to remove duplicates by modified date
else:
    fn_df = pd.read_csv(fn_df_csv)

fn_df = fn_df.sort_values(by="fn_date", ascending=False)
fn_df.drop_duplicates(subset="station", keep="first", inplace=True)
fn_df.reset_index()
### get rid of all the 'new edis'
fn_df = fn_df[~fn_df.fn_path.str.contains("modem")]
fn_df = fn_df[~fn_df.fn_path.str.contains("mtpy")]
fn_df = fn_df[~fn_df.fn_path.str.contains("shanes")]
fn_df = fn_df[~fn_df.fn_path.str.contains("kyhbar")]
fn_df = fn_df[~fn_df.fn_path.str.contains("bodie")]
fn_df.to_csv(os.path.join(edi_dirs[0], "all_edi_files_sorted.csv"))
