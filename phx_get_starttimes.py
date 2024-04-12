# -*- coding: utf-8 -*-
"""

Created on Wed Mar 27 17:08:05 2024

:author: Jared Peacock

:license: MIT

"""

from pathlib import Path
import pandas as pd

phx_path = Path(r"c:\MT\ST2024\phx")


entries = []
for fn in phx_path.iterdir():
    if fn.is_dir():
        data_path = fn.joinpath("Data")
        if not data_path.exists():
            data_path = fn

        for folder in data_path.iterdir():
            if folder.is_dir():
                if folder.name.count("-") == 3:
                    entry = {
                        "station": fn.stem,
                        "start": folder.name.split("_")[-1],
                    }
                    entries.append(entry)

df = pd.DataFrame(entries)
df.to_csv(phx_path.joinpath("start_times.csv"), index=False)
