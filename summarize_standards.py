# -*- coding: utf-8 -*-
"""
Created on Wed Jun 30 13:30:23 2021

@author: jpeacock
"""

# =============================================================================
# Imports
# =============================================================================
import inspect
import pandas as pd

from mt_metadata.base import BaseDict
from mt_metadata import timeseries
from mt_metadata.timeseries import filters
from mt_metadata.utils.validators import validate_attribute

ts_classes = dict(inspect.getmembers(timeseries, inspect.isclass))
flt_classes = dict(inspect.getmembers(filters, inspect.isclass))
# =============================================================================
# Summarize standards
# =============================================================================
def summarize_metadata_standards():
    """
    Summarize metadata standards into a dictionary
    """
    # need to be sure to make copies otherwise things will get
    # added in not great places.
    summary_dict = BaseDict()
    for key in ["survey", "station", "run", "electric", "magnetic", "auxiliary"]:
        obj = ts_classes[key.capitalize()]()
        summary_dict.add_dict(obj.attr_dict, key)
    
    for key in ["Coefficient", "FIR", "FrequencyResponseTable",
                "PoleZero", "TimeDelay"]:
        key += "Filter"
        obj = flt_classes[key]()
        summary_dict.add_dict(obj._attr_dict, validate_attribute(key))
    return summary_dict

def summarize_metadata_all_standards():
    """
    Summarize metadata standards into a dictionary
    """
    # need to be sure to make copies otherwise things will get
    # added in not great places.
    summary_dict = BaseDict()
    for key, obj in ts_classes.items():
        obj = obj()
        try:
            summary_dict.add_dict(obj._attr_dict,
                                  validate_attribute(key))
        except AttributeError:
            print(f"skipping {key}")
    
    for key in ["Coefficient", "FIR", "FrequencyResponseTable",
                "PoleZero", "TimeDelay"]:
        key += "Filter"
        obj = flt_classes[key]()
        summary_dict.add_dict(obj._attr_dict, validate_attribute(key))
    return summary_dict

def make_df(summary_dict):
    """
    Make a dataframe from the summary dict

    Parameters
    ----------
    summary_dict : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """

    entry_list = []
    for key in sorted(summary_dict.keys()):
        v_dict = summary_dict[key]
        entry = {"attribute": key}
        for dkey in ["description", "required", "type", "style", 
                     "units", "options", "alias", "example"]:
            value = v_dict[dkey]
            if value in [[], None, ]:
                value = ""
            elif isinstance(value, str):
                value = value.replace("", '').replace("[", "").replace("]", "")
            elif isinstance(value, list):
                value = ",".join(["{0}".format(ii) for ii in value])   
            
                
            entry[dkey] = value
            
        entry_list.append(entry)
            
    df = pd.DataFrame(entry_list)

    return df

df = make_df(summarize_metadata_all_standards())
df.to_csv(r"c:\Users\jpeacock\OneDrive - DOI\mt\mt_metadata\mt_timeseries_metadata_standard_v3.csv", 
          index=False)
