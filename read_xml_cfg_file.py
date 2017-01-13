# -*- coding: utf-8 -*-
"""
Created on Wed Jan 11 18:02:53 2017

@author: jpeacock
"""

cfg_fn = r"C:\Users\jpeacock\Documents\PyScripts\xml_cfg_test.cfg"

with open(cfg_fn, 'r') as fid:
    lines = fid.readlines()
    
    
cfg_dict = {}    
for line in lines:
    if line[0] == '#':
        pass
    elif line == '\n':
        pass
    else:
        line_list = line.strip().split('=')
        key = line_list[0].strip()
        value = line_list[1].strip()
        
        if key.find('.') > 0:
            key_list = key.split('.')
            if len(key_list) == 2:
                try:
                    cfg_dict[key_list[0]][key_list[1]] = value
                except KeyError:
                    cfg_dict[key_list[0]] = {key_list[1]:value}
            elif len(key_list) == 3:
                try: 
                    cfg_dict[key_list[0]][key_list[1]][key_list[2]] = value
                except KeyError:
                    try:
                        cfg_dict[key_list[0]][key_list[1]] = {key_list[2]:value}
                    except KeyError:
                        cfg_dict[key_list[0]] = {key_list[1]:{key_list[2]:value}}
        
        else:
            cfg_dict[key] = value

        
        