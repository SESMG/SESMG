#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to change resolution of timeseries values with constant
sampling rate.
"""

from __future__ import division
import os
import numpy as np
import math


def change_resolution(values, old_res, new_res, method="mean"):
    """
    Change the temporal resolution of values that have a constant sampling rate

    Parameters
    ----------
    values : array-like
        data points
    old_res : integer
        temporal resolution of the given values. old_res=3600 means
        hourly sampled data
    new_res : integer
        temporal resolution of the given data shall be converted to
    method : ``{"mean"; "sum"}``, optional
        - ``"mean"`` : compute mean values while resampling (e.g. for power).
        - ``"sum"``  : compute sum values while resampling (e.g. for energy).
    """
    # Compute original time indexes
    timeOld = np.arange(len(values)) * old_res

    # Compute new time indexes
    length = math.ceil(len(values) * old_res / new_res)
    timeNew = np.arange(length) * new_res

    # Sample means or sum values
    if method == "mean":
        # Interpolate
        valuesResampled = np.interp(timeNew, timeOld, values)
    else:
        # If values have to be summed up, use cumsum to modify the given data
        # Add one dummy value to later use diff (which reduces the number of
        # indexes by one)
        values = np.cumsum(np.concatenate(([0], values)))
        timeOld = np.concatenate((timeOld, [timeOld[-1] + old_res]))
        timeNew = np.concatenate((timeNew, [timeNew[-1] + new_res]))

        # Interpolate
        valuesResampled = np.interp(timeNew, timeOld, values)

        # "Undo" the cumsum
        valuesResampled = np.diff(valuesResampled)

    return valuesResampled


if __name__ == "__main__":
    values_old = np.arange(2000)
    dt_old = 60
    dt_new = 600
    values_new = change_resolution(values_old, dt_old, dt_new)

    #  Define src path
    src_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    #  Temperature - mean values
    try_filename = 'TRY2010_05_Jahr.dat'
    f_TRY = os.path.join(src_path, 'inputs', 'weather', try_filename)
    temp = np.loadtxt(f_TRY, skiprows=38, usecols=(8,))
    dt_temp_old = 3600
    dt_temp_short = 900
    dt_temp_long = 7200
    temp_long = change_resolution(temp, dt_temp_old, dt_temp_long)
    temp_short = change_resolution(temp, dt_temp_old, dt_temp_short)
