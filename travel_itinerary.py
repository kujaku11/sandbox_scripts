# -*- coding: utf-8 -*-
"""
Created on Sat Dec 09 14:07:05 2017

@author: jrpeacock
"""

fn = r"C:\Users\jrpeacock\Google Drive\honeymoon\nz_honeymoon_db.txt"

class Accommodation(object):
    def __init__(self, **kwargs):
        self.type = None
        self.name = None
        self.location = None
        self.checkin = None
        self.ref = None
        self.address = None
        
class Travel(object):
    def __init__(self, **kwargs):
        self.type = None
        self.arrive = None
        
class Move(object):
    def __init__(self, **kwargs):
        self.location = None
        self.
class action(object):
    def __init__(self, **kwargs):
        self.accommodation

with open(fn, 'r') as fid:
    lines = fid.readlines()
    
new_lines = []
for line in lines:
    line = line.strip()
    if line