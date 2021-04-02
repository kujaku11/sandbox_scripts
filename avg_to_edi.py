# -*- coding: utf-8 -*-
"""
Created on Thu Jul 23 16:53:15 2020

@author: jpeacock-pr
"""

import pandas as pd
from pathlib import Path
from mtpy.usgs import zonge
from mtpy.usgs import zen_processing as zp

station = 'um201'
station_int = station[2:]
# station_int = '0'
station_dir = Path(r"c:\MT\UM")
survey_cfg = station_dir.joinpath(station, f'{station}.cfg')
ext = 'dp'

# write config file
if not survey_cfg.exists():
    df = pd.read_csv(r"c:\MT\UM\{0}\{0}_processing_df.csv".format(station))
    scfg = zp.SurveyConfig()
    scfg.from_df(df)
    scfg.write_survey_config_file(survey_cfg)
    
za = zonge.ZongeMTAvg()
za.write_edi(r"c:\MT\UM\{0}\{1}\{1}{2}.avg".format(station, station_int, ext),
             station, 
             copy_path=r"c:\MT\UM\EDI_Files_birrp", 
             mtft_cfg_file=r"c:\MT\UM\{0}\mtft24.cfg".format(station),
             mtedit_cfg_file=r"c:\ZongePrograms\mtedit.cfg",
             survey_cfg_file=survey_cfg)