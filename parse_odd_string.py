# -*- coding: utf-8 -*-
"""
Created on Thu Feb 18 19:35:36 2021

:copyright: 
    Jared Peacock (jpeacock@usgs.gov)

:license: MIT

"""

s = "author: machine generated, comments: A.Kelbert:Gap and a spike 726 secs into the run. Poor quality data after this event. However, timing before and after the gap verified against CAV09."
# s = "a: b, c:d"
# s = "a: b, c: d, efg"
def parse(t, filled={}):
    k, *other = t.split(":", 1)
    if other: 
        other = other[0]
        key = k
        if other.find(':') >= 0 and other.find(",") >= 0:
            if other.find(':') < other.find(','):
                print(": < ," + other)
                if other.count(':') > 1:
                    value, *maybe = other.split(',', 1)
                    filled[key] = value.strip()
                    if maybe:
                        filled = parse(maybe[0].strip(), filled)
                else:
                    filled[key] = other
            else:
                print(": > ," + other)
                value, *maybe = other.split(',', 1)
                filled[key] = value.strip()
                if maybe:
                    filled = parse(maybe[0].strip(), filled)
        elif other.find(':') > 0:
            print(': > 0|' + other)
            value, *maybe = other.split(':', 1)
            filled[key] = value.strip()
        else:
            filled[key] = other.strip()
                
    else:
        filled[k] = None
    return filled

d = parse(s)