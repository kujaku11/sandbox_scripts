# -*- coding: utf-8 -*-
"""
Created on Wed Jan 07 10:11:16 2015

@author: jpeacock-pr
"""

import PIL.Image as Image
import os

base_map_fn = r"c:\Users\jpeacock-pr\Documents\ParaviewFiles\mb_mt\Maps\geology_overlay_nov_no_dem.png"


im = Image.open(base_map_fn)

# bbox (0, 0, 1082, 782)
#im.show()

# profile 1 bbox
#new_base_map_fn = os.path.join(os.path.dirname(base_map_fn), 
#                               'profile1_geology_overlay_no_dem.png')
#im2 = im.crop((25, 0, 1082, 450))
#im2.show()
#im2.save(new_base_map_fn) 

## profile 2 bbox
#new_base_map_fn = os.path.join(os.path.dirname(base_map_fn), 
#                               'profile2_geology_overlay_no_dem.png')
#im2 = im.crop((25, 0, 1082, 355))
#im2.show()
#im2.save(new_base_map_fn) 

## profile 3 bbox
#new_base_map_fn = os.path.join(os.path.dirname(base_map_fn), 
#                               'profile3_geology_overlay_no_dem.png')
#im2 = im.crop((25, 0, 1082, 242))
#im2.show()
#im2.save(new_base_map_fn) 


# profile 4 bbox
new_base_map_fn = os.path.join(os.path.dirname(base_map_fn), 
                               'profile4_geology_overlay_no_dem.png')
im2 = im.crop((25, 0, 1082, 190))
im2.show()
im2.save(new_base_map_fn) 
