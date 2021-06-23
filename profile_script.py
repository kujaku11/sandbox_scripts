# -*- coding: utf-8 -*-
"""
Created on Mon Dec 10 16:53:51 2018

@author: jpeacock
"""

import cProfile, pstats, io
from archive.archive import Capturing

# =============================================================================
# class for capturing the output to store in a file
# =============================================================================
# this should capture all the print statements
class Capturing(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = io.StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        sys.stdout = self._stdout

def profile(fnc):
    
    def inner(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()
        retval = fnc(*args, **kwargs)
        pr.disable()
        s = io.StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())
        return retval

    return inner

@profile
def code_to_profile():    
    "code to profile"
    
with Capturing() as output:   
    %time code_to_profile()

with open(r"logile_fn.log", "w") as fid:
    fid.write("\n".join(output))
    

