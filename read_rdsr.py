# -*- coding: utf-8 -*-
"""
Created on Sun Sep 12 15:18:32 2021

@author: jpeacock
"""
from pathlib import Path
import pandas as pd

fn = Path(r"c:\Users\jpeacock\OneDrive - DOI\RDSR\RDSR_IPDS_report_bedrosian.csv")
df = pd.read_csv(fn.as_posix())

df.rename(columns=dict([(name, name.replace(' ', '_').lower()) for name in df.columns]), 
          inplace=True)
df["approved_on"] = pd.to_datetime(df["approved_on"])
df = df.sort_values(by="approved_on")

lines = []
for row in df.itertuples():
    lines.append(
        f"{row.working_title}\n\tIP-{row.ip_number:06}, BOA:{row.approved_on.date().isoformat()} DOI:{row.doi}\n{'-'*50}\n")
    
txt_fn = fn.parent.joinpath(f"{fn.stem}.txt")
with open(txt_fn, encoding="utf-8", mode="w") as fid:
    fid.write("\n".join(lines))
