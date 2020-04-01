# -*- coding: utf-8 -*-
"""
Created on Tue Mar 31 10:08:23 2020

@author: jpeacock
"""

from mtpy.usgs import zen
from mtpy.core import ts
from pathlib import Path
import datetime
import pandas as pd
import numpy as np

fn_path = Path(r"c:\Users\jpeacock\Documents\imush\G016")
sampling_rate = 4
t_buffer = 8*3600

### need to get all the files for one channel
fn_dict = dict([(key, []) for key in ['ex', 'ey', 'hx', 'hy', 'hz']])

for fn in fn_path.glob('*.Z3D'):
    z_obj = zen.Zen3D(fn)
    z_obj.read_all_info()
    
    fn_dict[z_obj.component].append({'start':z_obj.zen_schedule.isoformat(), 
                                     'df':z_obj.df,
                                     'fn':z_obj.fn})
    
# for comp, fn_list in fn_dict.items():
fn_list = fn_dict['ex']
comp_df = pd.DataFrame(fn_list)
### sort the data frame by date
comp_df = comp_df.sort_values('start')

start_dt = datetime.datetime.fromisoformat(comp_df.start.min())
end_dt = datetime.datetime.fromisoformat(comp_df.start.max())
t_diff = (end_dt - start_dt).total_seconds()

new_ts = ts.MTTS()
new_ts.ts = np.zeros(int((t_diff + t_buffer) * sampling_rate))
new_ts.sampling_rate = sampling_rate
new_ts.start_time_utc = start_dt

for index, row in comp_df.iterrows():
    z_obj = zen.Zen3D(row['fn'])
    z_obj.read_z3d()
    t_obj = z_obj.ts_obj
    t_obj.decimate(int(z_obj.df/sampling_rate))
    new_ts.ts.data[(new_ts.ts.index >= t_obj.ts.index[0]) & 
                    (new_ts.ts.index <= t_obj.ts.index[-1])] = t_obj.ts.data
