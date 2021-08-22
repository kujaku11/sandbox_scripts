# -*- coding: utf-8 -*-
"""
Created on Mon Feb 06 15:57:59 2017

@author: jpeacock
"""

from pathlib import Path
import mtpy.usgs.zen as zen

# station_folder = Path(r"c:\MT\Katmai2021\KAT027")
station_folder = Path(r"/mnt/hgfs/MT_Data/Katmai2021/KAT027")

<<<<<<< HEAD
for fn in station_folder.rglob("*.z3d"):
    z3d_obj = zen.Zen3D(fn)
    z3d_obj.read_all_info()
    
    station = f"KAT{int(z3d_obj.station):03}"
    channel = z3d_obj.metadata.ch_cmp.upper()
    st = z3d_obj.schedule.Time.replace(':','')
    sd = z3d_obj.schedule.Date.replace('-','')
    sv_fn = station_folder.joinpath('{0}_{1}_{2}_{3}_{4}.Z3D'.format(station,
                                             sd, 
                                             st, 
                                             int(z3d_obj.df),
                                             channel))
    
    
    fn.replace(sv_fn)
              
    print('renamed {0} to {1}'.format(fn, sv_fn))
=======
for fn in os.listdir(station_folder):
    if fn.endswith(".Z3D"):
        z3d_obj = zen.Zen3D(os.path.join(station_folder, fn))
        z3d_obj.read_all_info()

        station = os.path.basename(station_folder)
        channel = z3d_obj.metadata.ch_cmp.upper()
        st = z3d_obj.schedule.Time.replace(":", "")
        sd = z3d_obj.schedule.Date.replace("-", "")
        sv_fn = "{0}_{1}_{2}_{3}_{4}.Z3D".format(
            station, sd, st, int(z3d_obj.df), channel
        )

        os.rename(os.path.join(station_folder, fn), os.path.join(station_folder, sv_fn))

        print "renamed {0} to {1}".format(fn, sv_fn)
>>>>>>> b0c68cef252e657cf5a2e7b8832e90511d030330
