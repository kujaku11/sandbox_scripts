# -*- coding: utf-8 -*-
"""

Copy the correct files into one station folder from SPIA.  

1) edit the TEM response, then run the inversion smooth or blocky
   This creates a folder that has an .emo file which has nearly everything 
   you want, but doesn't calculate the forward responses
2) if satisfied with the result, go into the inversion and click edit, this
   will create the foward responses to compare with the data.

3) run this script which picks out the 2 folders containing the inversion 
   results and the forward response assuming no more inversions or edits are
   done.

Created on Tue Jul 28 09:52:56 2020

:author: Jared Peacock

:license: MIT

"""

from pathlib import Path
import shutil

station = 'T32'
inv_type = 'blocky'
inv_dir = Path(r"c:\Users\peaco\Documents\MT\UM2020\TEM\Project162\AarhusInvFiles\20200728")
save_dir = Path(r"c:\Users\peaco\Documents\MT\UM2020\TEM\models\{0}\{1}".format(inv_type,
                                                                                station))
remove_dir = True

# get the inversion and forward model files
inv_folders = sorted(inv_dir.iterdir())[-3:-1]

# reverse order to make sure the inversion files are written last
for folder in inv_folders[::-1]:
    for fn in folder.iterdir():
        if fn.suffix in ['.emo', '.ite', '.log', '.fwr', '.mod', '.tem']:
            shutil.copy(fn, save_dir.joinpath(fn.name))
            print('Copied {0} to {1}'.format(fn.name, save_dir.joinpath(fn.name)))

if remove_dir:           
    shutil.rmtree(inv_dir)
            
