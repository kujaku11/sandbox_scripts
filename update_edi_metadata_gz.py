# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 16:16:13 2018

@author: jpeacock
"""

import os
import mtpy.core.mt as mt
import pandas as pd

edi_path = r"d:\Peacock\MTData\Geysers\EDI_Files_birrp\Edited\geographic_north"
birrp_cfg = r"D:\Peacock\MTData\Geysers\gz_birrp.cfg"
survey_csv = r"d:\Peacock\MTData\Geysers\Archive\survey_summary.csv"
quality_csv = r"d:\Peacock\MTData\Geysers\Archive\tf_quality.csv"


sv_path = os.path.join(edi_path, "final_edi")
png_path = os.path.join(edi_path, "final_png")
if not os.path.exists(sv_path):
    os.mkdir(sv_path)
if not os.path.exists(png_path):
    os.mkdir(png_path)

df = pd.read_csv(survey_csv)
quality_df = pd.read_csv(quality_csv, names=["station", "quality"])

for fn in os.listdir(edi_path):
    if not fn.endswith(".edi"):
        continue

    mt_obj = mt.MT(fn=os.path.join(edi_path, fn))
    birrp_index = mt_obj.Notes.info_list.index("***birrp parameters***") + 1
    mt_obj.Notes.info_list = mt_obj.Notes.info_list[birrp_index:]
    mt_obj.Notes.info_dict = {}
    for info_str in mt_obj.Notes.info_list:
        try:
            key, value = info_str.split("=", 1)
        except ValueError:
            continue
        if key in ["n_samples", "ofil", "prej"]:
            continue
        elif (
            "fieldnotes" in key
            or "provenance" in key
            or "processing" in key
            or "copyright" in key
        ):
            continue
        else:
            b_obj = setattr(
                mt_obj.Processing.Software, "param_{0}".format(key), value.strip()
            )
    #            key = 'processing.birrp.{0}'.format(key)
    #        mt_obj.Notes.info_dict[key.strip()] = value.strip()
    mt_obj.read_cfg_file(birrp_cfg)
    mt_obj.Copyright.Citation.author = ",".join(mt_obj.Copyright.Citation.author)
    mt_obj.Copyright.Citation.title = ",".join(mt_obj.Copyright.Citation.title)

    ### read info from survey
    sdf = df.loc[df.index[df.station == mt_obj.station.lower()]]
    if len(sdf.index) == 0:
        print("Did not find {0} in survey file".format(mt_obj.station))
    else:
        for comp in ["ex", "ey", "hx", "hy", "hz"]:
            cols = [col for col in df.columns if comp + "_" in col]
            if "e" in comp:
                c_obj = getattr(mt_obj.FieldNotes, "Electrode_{0}".format(comp))
            elif "h" in comp:
                c_obj = getattr(mt_obj.FieldNotes, "Magnetometer_{0}".format(comp))
            for col in ["length", "azimuth"]:
                setattr(c_obj, col, sdf["{0}_{1}".format(comp, col)].values[0])
        mt_obj.FieldNotes.DataLogger.id = sdf.instrument_id.values[0]
        mt_obj.FieldNotes.DataLogger.start_date = sdf.start_date.values[0]
        mt_obj.FieldNotes.DataLogger.end_date = sdf.stop_date.values[0]
    try:
        qf = quality_df[quality_df.station == mt_obj.station]["quality"].values[0]
        mt_obj.FieldNotes.DataQuality.rating = qf
        mt_obj.FieldNotes.DataQuality.good_from_period = "0.002"
        mt_obj.FieldNotes.DataQuality.good_to_period = "1024"
    except IndexError as error:
        print(
            "{0} No quality factor for {1}, setting to 4".format(error, mt_obj.station)
        )

    ### Write file
    mt_obj.write_mt_file(save_dir=sv_path)

    # plot response
    if mt_obj.station.lower() == "gz05":
        pr = mt_obj.plot_mt_response(plot_num=2)
        pr.save_plot(os.path.join(png_path, mt_obj.station + ".png"), fig_dpi=300)
