# -*- coding: utf-8 -*-
"""
Created on Thu Jun  8 12:37:40 2023

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
from pathlib import Path
import copy
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# from matplotlib.gridspec import GridSpec
from pathlib import Path
from scipy import signal
from scipy.optimize import minimize

from mth5.io.zen import CoilResponse
from mt_metadata.timeseries.filters import PoleZeroFilter

# =============================================================================


class Extrapolate:
    def __init__(self, fap_filter, **kwargs):
        self.fap = fap_filter
        self.n_poles = 5
        self.n_zeros = 2
        self.seed = 1
        self.method = "Powell"

        for key, value in kwargs.items():
            setattr(self, key, value)

        np.random.seed(self.seed)

    @property
    def angular_frequencies(self):
        return 2 * np.pi * self.fap.frequencies

    @property
    def complex_response(self):
        return self.fap.complex_response(self.fap.frequencies)

    def get_data_vector(self):
        """

        :return: DESCRIPTION
        :rtype: TYPE

        """

        b0 = np.random.rand(self.n_zeros + 1)
        a0 = np.random.rand(self.n_poles + 1)

        return np.hstack((b0, a0))

    def objective_function(self, model_vector):
        """

        :param fap_filter: DESCRIPTION
        :type fap_filter: TYPE
        :param n_poles: DESCRIPTION, defaults to 3
        :type n_poles: TYPE, optional
        :param n_zeros: DESCRIPTION, defaults to 1
        :type n_zeros: TYPE, optional
        :param method: DESCRIPTION, defaults to "Powell"
        :type method: TYPE, optional
        :return: DESCRIPTION
        :rtype: TYPE

        """

        b1 = model_vector[: self.n_zeros + 1]
        a1 = model_vector[self.n_zeros + 1 :]

        w, h = signal.freqs(b1, a1, worN=self.angular_frequencies)
        residual = self.complex_response - h
        misfit = np.sqrt(np.mean(np.abs(residual**2)))

        return misfit

    def fit(self):
        """

        :param fap_filter: DESCRIPTION
        :type fap_filter: TYPE
        :param n_poles: DESCRIPTION, defaults to 3
        :type n_poles: TYPE, optional
        :param n_zeros: DESCRIPTION, defaults to 1
        :type n_zeros: TYPE, optional
        :param seed: DESCRIPTION, defaults to 1
        :type seed: TYPE, optional
        :param method: DESCRIPTION, defaults to "Powell"
        :type method: TYPE, optional
        :param xatol: DESCRIPTION, defaults to 1E-10
        :type xatol: TYPE, optional
        :return: DESCRIPTION
        :rtype: TYPE

        """

        residual = minimize(
            self.objective_function,
            self.get_data_vector(),
            method=self.method,
            options={"disp": True},
        )

        return self.to_zpk_filter(residual)

    def to_zpk_filter(self, residual):
        b = residual.x[: self.n_zeros + 1]
        a = residual.x[self.n_zeros + 1 :]
        zpk = signal.TransferFunction(b, a).to_zpk()

        zpk_filter = PoleZeroFilter()
        zpk_filter.poles = zpk.poles
        zpk_filter.zeros = zpk.zeros
        zpk_filter.gain = zpk.gain

        zpk_filter.units_in = self.fap.units_in
        zpk_filter.units_out = self.fap.units_out
        zpk_filter.name = self.fap.name
        zpk_filter.instrument_type = self.fap.instrument_type
        zpk_filter.calibration_date = self.fap.calibration_date

        return zpk_filter


# =============================================================================
# Run
# =============================================================================
cal_fn = Path(r"c:\Users\jpeacock\OneDrive - DOI\MTData\antenna_20190411.cal")

c = CoilResponse()
c.read_antenna_file(cal_fn)

fap = c.get_coil_response_fap(2284)
pz = Extrapolate(fap)

r = pz.fit()
r.plot_response(np.logspace(3, -5, 100))
