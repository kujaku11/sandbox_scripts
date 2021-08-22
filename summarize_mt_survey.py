#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 31 09:05:45 2020

@author: peacock
"""


from mtpy.usgs import zen
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib import dates
import datetime

survey_path = Path(r"/mnt/hgfs/MT/MusicValley")
csv_path = Path(r"/mnt/hgfs/MT/MusicValley/survey_summary_small.csv")

df_dict = {
    256: datetime.timedelta(hours=7, minutes=45),
    4096: datetime.timedelta(minutes=15),
    1024: datetime.timedelta(minutes=10),
}

if not csv_path.exists():

    schedule_dict = ""

    date_dict = []

    for station in survey_path.glob("**/*"):
        station_path = Path.joinpath(survey_path.parent, survey_path.name, station)
        for z3d_fn in station_path.glob("*.Z3D"):
            z_obj = zen.Zen3D(
                Path.joinpath(station_path.parent, station_path.name, z3d_fn)
            )
            try:
                z_obj.read_all_info()
            except zen.ZenGPSError:
                continue

            entry = {
                "station": z_obj.station,
                "start_date": z_obj.zen_schedule.isoformat(),
                "sampling_rate": z_obj.df,
            }
            date_dict.append(entry)

    df = pd.DataFrame(date_dict)
    df.drop_duplicates(["station", "start_date"], inplace=True)
    df = df.sort_values(["start_date", "station"], inplace=False)
    df.to_csv(csv_path, index=False)

else:
    df = pd.read_csv(csv_path.absolute())

survey_01 = df[df.start_date < "2020-01-01T00:00:00"]
survey_02 = df[df.start_date > "2016-01-01T00:00:00"]
x_ticks = survey_02.start_date.to_list()

fig = plt.figure()
ax1 = fig.add_subplot(1, 1, 1)

sr = 256
count = 0
for index, row in survey_02.iterrows():
    sd = datetime.datetime.fromisoformat(row["start_date"])
    end_time = (sd + df_dict[row["sampling_rate"]]).isoformat()
    if row["sampling_rate"] != sr:
        sr = row["sampling_rate"]
        count = 0
    else:
        count += 1

    if row["sampling_rate"] == 256:
        color = (0.9, 0.9, 1)
    elif row["sampling_rate"] == 4096:
        color = (1, 0.9, 0.9)
    else:
        continue
    # text_y = datetime.datetime.fromisoformat(row['start_date']) - \
    #         datetime.timedelta(seconds=10)

    if sr == 4096:
        xdata = count + 8
    else:
        xdata = count

    ax1.plot_date(
        [row["start_date"], end_time],
        [xdata, xdata],
        color=color,
        xdate=True,
        ydate=False,
        ls="-",
        lw=10,
        ms=20,
    )
    ax1.text(
        row["start_date"],
        xdata,
        row["station"][2:],
        ha="center",
        va="center",
        fontdict={"weight": "bold", "size": 6},
    )

ax1.xaxis.set_tick_params(rotation=90, labelsize=8)
ax1.set_xticks(x_ticks)
ax1.set_xlim([min(x_ticks), max(x_ticks)])
fig.tight_layout()

# ax1.xaxis.set_major_formatter(dates.DateFormatter('%Y-%m-%d %H:%M:%S'))
plt.show()
