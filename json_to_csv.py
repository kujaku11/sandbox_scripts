# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 12:48:31 2020

@author: jpeacock
"""
import json
import csv
from pathlib import Path

j_fn = r"c:\Users\jpeacock\Documents\GitHub\mt2ph5\metadata\channel_metadata.json"
j_path = Path(j_fn)
csv_fn = Path(j_path.with_suffix('').as_posix() + '.csv')


with open(j_fn, 'r') as fid:
    j_dict = json.load(fid)
    
    
with open(csv_fn, 'w', newline='') as csv_fid:
    field_names = list(j_dict.keys())
    write = csv.writer(csv_fid)
    for key, value in j_dict.items():
        write.writerow([key, value])
        
    
    # with open('names.csv', 'w', newline='') as csvfile:
    # fieldnames = ['first_name', 'last_name']
    # writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    # writer.writeheader()
    # writer.writerow({'first_name': 'Baked', 'last_name': 'Beans'})
    # writer.writerow({'first_name': 'Lovely', 'last_name': 'Spam'})
    # writer.writerow({'first_name': 'Wonderful', 'last_name': 'Spam'})