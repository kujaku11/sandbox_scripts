# -*- coding: utf-8 -*-
"""
Created on Thu Apr  4 15:12:00 2019

@author: jpeacock
"""
import glob
import pandas as pd
from mtpy.core import mt

edi_dir = r"d:\Peacock\MTData\GabbsValley\final_edi"
quality_fn = r"d:\Peacock\MTData\GabbsValley\final_edi\tf_quality.csv"

edi_list = glob.glob(edi_dir + "\*.edi")
quality_df = pd.read_csv(quality_fn, names=["station", "quality"])

for edi in edi_list:
    mt_obj = mt.MT(edi)
    try:
        qf = quality_df[quality_df.station == mt_obj.station]["quality"].values[0]
    except IndexError as error:
        print(
            "{0} No quality factor for {1}, setting to 4".format(error, mt_obj.station)
        )

    mt_obj.FieldNotes.DataQuality.rating = qf
    mt_obj.FieldNotes.DataQuality.good_from_period = "0.002"
    mt_obj.FieldNotes.DataQuality.good_to_period = "1024"
    mt_obj.FieldNotes.Electrode_ex.x2 = 50.0
    mt_obj.FieldNotes.Electrode_ey.y2 = 50.0
    mt_obj.Site.loc = "Gabbs Valley, Nevada"

    mt_obj.write_mt_file()
