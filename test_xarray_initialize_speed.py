# -*- coding: utf-8 -*-
"""
Created on Fri Feb  2 13:16:42 2024

@author: jpeacock
"""

# =============================================================================
# Imports
# =============================================================================
import numpy as np
import xarray as xr

# =============================================================================
periods = np.array([100])
# create an empty array for the transfer function
tf = xr.DataArray(
    data=0 + 0j,
    dims=["period", "output", "input"],
    coords={
        "period": periods,
        "output": ["ex", "ey", "hz"],
        "input": ["hx", "hy"],
    },
    name="transfer_function",
)

tf_err = xr.DataArray(
    data=0,
    dims=["period", "output", "input"],
    coords={
        "period": periods,
        "output": ["ex", "ey", "hz"],
        "input": ["hx", "hy"],
    },
    name="transfer_function_error",
)

tf_model_err = xr.DataArray(
    data=0,
    dims=["period", "output", "input"],
    coords={
        "period": periods,
        "output": ["ex", "ey", "hz"],
        "input": ["hx", "hy"],
    },
    name="transfer_function_model_error",
)

inv_signal_power = xr.DataArray(
    data=0 + 0j,
    dims=["period", "output", "input"],
    coords={
        "period": periods,
        "output": ["hx", "hy"],
        "input": ["hx", "hy"],
    },
    name="inverse_signal_power",
)

residual_covariance = xr.DataArray(
    data=0 + 0j,
    dims=["period", "output", "input"],
    coords={
        "period": periods,
        "output": ["ex", "ey", "hz"],
        "input": ["ex", "ey", "hz"],
    },
    name="residual_covariance",
)
# tf = xr.DataArray(
#     data=0 + 0j,
#     dims=["period", "output", "input"],
#     coords={
#         "period": periods,
#         "output": ["ex", "ey", "hz", "hx", "hy"],
#         "input": ["ex", "ey", "hz", "hx", "hy"],
#     },
#     name="transfer_function",
# )

# tf_err = xr.DataArray(
#     data=0,
#     dims=["period", "output", "input"],
#     coords={
#         "period": periods,
#         "output": ["ex", "ey", "hz", "hx", "hy"],
#         "input": ["ex", "ey", "hz", "hx", "hy"],
#     },
#     name="transfer_function_error",
# )

# tf_model_err = xr.DataArray(
#     data=0,
#     dims=["period", "output", "input"],
#     coords={
#         "period": periods,
#         "output": ["ex", "ey", "hz", "hx", "hy"],
#         "input": ["ex", "ey", "hz", "hx", "hy"],
#     },
#     name="transfer_function_model_error",
# )

# inv_signal_power = xr.DataArray(
#     data=0 + 0j,
#     dims=["period", "output", "input"],
#     coords={
#         "period": periods,
#         "output": ["ex", "ey", "hz", "hx", "hy"],
#         "input": ["ex", "ey", "hz", "hx", "hy"],
#     },
#     name="inverse_signal_power",
# )

# residual_covariance = xr.DataArray(
#     data=0 + 0j,
#     dims=["period", "output", "input"],
#     coords={
#         "period": periods,
#         "output": ["ex", "ey", "hz", "hx", "hy"],
#         "input": ["ex", "ey", "hz", "hx", "hy"],
#     },
#     name="residual_covariance",
# )

# will need to add in covariance in some fashion
ds = xr.Dataset(
    {
        tf.name: tf,
        tf_err.name: tf_err,
        tf_model_err.name: tf_model_err,
        inv_signal_power.name: inv_signal_power,
        residual_covariance.name: residual_covariance,
    },
    coords={
        "period": periods,
        "output": ["ex", "ey", "hz", "hx", "hy"],
        "input": ["ex", "ey", "hz", "hx", "hy"],
    },
)
