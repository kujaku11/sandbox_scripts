# -*- coding: utf-8 -*-
"""
Created on Fri Aug 14 09:09:51 2015

@author: jpeacock
"""
import os
import shutil

usb_drive = r"/media/jpeacock/USGS_MT/Peacock/MB_June2015"
save_drive = r"/mnt/hgfs/MTData"

save_dir = os.path.join(save_drive, os.path.basename(usb_drive))
if not os.path.exists(save_dir):
    os.mkdir(save_dir)
    
for folder in os.listdir(usb_drive):
    if os.path.isdir(os.path.join(usb_drive, folder)) is True:
        save_folder = os.path.join(save_dir, folder)
        if not os.path.exists(save_folder):
            os.mkdir(save_folder)
            for fn in os.listdir(os.path.join(usb_drive, folder)):
                usb_fn = os.path.join(usb_drive, folder, fn)
                if os.path.isfile(usb_fn) is True:
                    sv_fn = os.path.join(save_folder, fn)
                    shutil.copy(usb_fn, sv_fn)
                    
    elif os.path.isfile(os.path.join(usb_drive, folder)) is True:
        usb_fn = os.path.join(usb_drive, folder)
        sv_fn = os.path.join(save_dir, folder)
        shutil.copy(usb_fn, sv_fn)
        

