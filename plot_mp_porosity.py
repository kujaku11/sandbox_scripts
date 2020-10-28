# -*- coding: utf-8 -*-
"""
Created on Tue Oct 29 15:22:13 2019

@author: jpeacock
"""

import pandas as pd

fn = r"c:\Users\jpeacock\OneDrive - DOI\MountainPass\papers\ofr20161070_table02_rock_property_data.csv"

df = pd.read_csv(fn, usecols=["ID", "LAT", "LONG", "RT", "SBD", "POR", "AGE"])
