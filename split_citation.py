# -*- coding: utf-8 -*-
"""
Created on Wed Apr 21 10:35:59 2021

:copyright: 
    Jared Peacock (jpeacock@usgs.gov)

:license: MIT

"""


def split_names(string):
    slist = string.split(',')
    
    names = []
    for last, first in zip(slist[::2], slist[1::2]):
        first = first.strip()
        last = last.strip()
        if '.' in last:
            if last[last.find('.') + 1] != ' ':
                last = last.replace('.', '. ')
            names.append(f"{last} {first}")
        elif '.' in first:
            if first[first.find('.') + 1] != ' ':
                first = first.replace('.', '. ')
            names.append(f"{first.strip()} {last}")
            
    return ' and '.join(names)
            
s = "Faulds, J.E., Craig, J.W., Hinz, N.H., Coolbaugh, M.F., Glen, J.M.G., Earney, T.E., Schermerhorn, W.D., Peacock, J.R., Deoreo, S.B., Siler, D.L."

authors = split_names(s)        
            
    

