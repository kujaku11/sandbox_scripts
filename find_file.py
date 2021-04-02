# -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 16:02:19 2019

@author: jpeacock
"""

import os, glob

root_dir = r"d:\\Peacock_Backup"
fn_basename = r"gabbs*"

result = []
for root, dirs, files in os.walk(root_dir):
    find = glob.glob("{0}\{1}".format(root, fn_basename))
    if len(find) > 0:
        print("=" * 50)
        print(find)
#    if fn_basename in files:
#
#        print('  Found in {0}'.format(os.path.join(root, fn_basename)))
