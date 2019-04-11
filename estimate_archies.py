# -*- coding: utf-8 -*-
"""
Created on Tue Apr  9 16:06:21 2019

@author: jpeacock
"""

import numpy as np

def archies(sigma_measured, porosity, saturation, n=2, m=2, alpha=1):
    """
    modified archies law
    """
    
    sigma_w = (sigma_measured * alpha * saturation**n) / porosity**m
    
    return sigma_w

def sigma_fluid(sigma_zero, initial_temperature, salinty, temperature):
    """
    
    """
    sigma_f = (sigma_zero * (initial_temperature + 21.5)) / (temperature + 21.5)
    
    return sigma_f