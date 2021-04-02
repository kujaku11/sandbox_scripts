# -*- coding: utf-8 -*-
"""
Created on Fri Apr 26 16:44:42 2019

@author: jpeacock
"""
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import pandas as pd


class RockPhase(object):
    """
    simple class for a rock phase
    """

    def __init__(self, sigma=None, phi=None, m=None, **kwargs):
        self.sigma = sigma
        self.phi = phi
        self.m = m

        for key, item in kwargs.items():
            setattr(self, key, item)

    def from_dict(self, phase_dict):
        """
        read in values from dictionary
        """
        for key, item in phase_dict.items():
            setattr(self, key, item)

    def is_phase(self):
        """
        test if all attributes are full
        """

        if (
            type(self.sigma) is type(None)
            and type(self.phi) is type(None)
            and type(self.m) is type(None)
        ):
            return False
        else:
            return True

    def calculate_phase(self):
        """
        calculate the contribution of a given phase
        """
        if self.is_phase():
            return self.sigma * self.phi ** self.m
        else:
            return 0


class Glover(object):
    """
    estimate modified archies equation for multiple phases
    """

    def __init__(self):
        self._max_phase = 4

        for ii in range(self._max_phase):
            setattr(self, "phase_{0:02}".format(ii + 1), RockPhase())

    @property
    def num_phases(self):
        """
        get the number of phases
        """
        num_phases = 0
        for ii in range(self._max_phase):
            if getattr(self, "phase_{0:02}".format(ii + 1)).is_phase():
                num_phases += 1
        return num_phases

    def estimate_resistivity(self):
        """
        estimate resistivity from different given phases
        """
        res = 0
        for ii in range(self.num_phases):
            phase = getattr(self, "phase_{0:02}".format(ii + 1))
            res += phase.calculate_phase()

        return 1.0 / res

    @property
    def x(self):
        """
        get the x axis 
        """
        x = self.phase_01.phi
        if type(x) is float:
            x = np.array([x])
        for ii in range(self.num_phases):
            phase = getattr(self, "phase_{0:02}".format(ii + 1))
            try:
                if len(phase.phi) > len(x):
                    x = phase.phi
            except TypeError:
                pass

        return x


def fit_distribution(x_data, params, distribution):
    """
    fit data for a given distribution
    """

    dist = getattr(stats, distribution)
    if len(params) == 2:
        pdf = dist.pdf(x_data, params[0], params[1])
        pdf_min, pdf_max = dist.interval(0.5, params[0], params[1])

    elif len(params) == 3:
        pdf = dist.pdf(x_data, params[0], params[1], params[2])
        pdf_min, pdf_max = dist.interval(0.5, params[0], params[1], params[2])

    elif len(params) == 4:
        pdf = dist.pdf(x_data, params[0], params[1], params[2], params[3])
        pdf_min, pdf_max = dist.interval(
            0.5, params[0], params[1], params[2], params[3]
        )

    return pdf, pdf_min, pdf_max


def get_best_distribution(
    data,
    dist_names=[
        "norm",
        "exponweib",
        "weibull_max",
        "weibull_min",
        "genextreme",
        "lognorm",
    ],
):

    dist_results = []
    params = {}
    for dist_name in dist_names:
        dist = getattr(stats, dist_name)
        param = dist.fit(data)

        params[dist_name] = param
        # Applying the Kolmogorov-Smirnov test
        D, p = stats.kstest(data, dist_name, args=param)
        dist_results.append((dist_name, p))

    # select the best fitted distribution
    best_dist, best_p = max(dist_results, key=lambda item: item[1])

    return best_dist, best_p, params[best_dist]


def get_layer_depth(layer_name):
    """
    get the layer depth from given name
    """
    find_01 = layer_name.find("_") + 1
    if layer_name.count("m") > 1:
        find_02 = layer_name.find("m", 4)
        find_01 += 1
        scale = -1
    else:
        find_02 = layer_name.find("m")
        scale = 1
    depth = int(layer_name[find_01:find_02]) * scale
    return depth


def get_layers(layer_list, depth):
    """
    get only the layers for the given geology
    """

    layer_dict = dict([(layer, get_layer_depth(layer)) for layer in layer_list])
    return_list = []
    if depth[0] is None:
        for layer, l_depth in layer_dict.items():
            if l_depth <= depth[1]:
                return_list.append(layer)
    else:
        for layer, l_depth in layer_dict.items():
            if l_depth >= depth[0] and l_depth <= depth[1]:
                return_list.append(layer)

    return return_list
