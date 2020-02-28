#!/usr/bin/env python
# coding=utf-8
"""
Script to load radiation of TRY weather files
"""

import os
import numpy as np


def load_try_data(path_try=None):
    """
    Returns TRY dataset

    Parameters
    ----------
    path_try : str, optional
        Defines path to TRY file (default: None). If set to None, uses
        default TRY dataset (TRY 2010, region 5)

    Returns
    -------
    try_data : numpy array
        Numpy array with TRY data
    """

    # Generate TRY path (if path is None) and use TRY2010_05_Jahr.dat
    if path_try is None:
        src_path = os.path.dirname(os.path.dirname(__file__))
        pathTRY = os.path.join(src_path,
                               'inputs',
                               'weather',
                               'TRY2010_05_Jahr.dat')

    # Read TRY data
    try_data = np.genfromtxt(pathTRY, skip_header=38)

    return try_data


def get_rad_from_try_data(try_data):
    """
    Returns direct and diffuse radiation of TRY datasets

    Parameters
    ----------
    try_data : numpy array
        Numpy array with TRY data

    Returns
    -------
    tuple_rad : tuple (of arrays)
        Tuple holding direct and diffuse radiation arrays
        (q_direct, q_diffuse) in W/m^2
    """

    #  Number of rows
    nb_rows = 8760

    q_direct = try_data[0:nb_rows, 13]
    q_diffuse = try_data[0:nb_rows, 14]

    #  Just in case :-)
    #  t_ambient = = try_data[0:nb_rows, 8]
    # v_wind = try_data[0:nb_rows, 7]
    # cloudiness = try_data[0:nb_rows, 5]
    # rad_sky = try_data[0:nb_rows, 16]
    # rad_earth = try_data[0:nb_rows, 17]

    return (q_direct, q_diffuse)


def get_rad_from_try_path(path_try=None):
    """
    Loads TRY dataset and returns direct and diffuse radiation.
    Default files are returned with 3600 seconds resolution

    Parameters
    ----------
    path_try : str, optional
        Defines path to TRY file (default: None). If set to None, uses
        default TRY dataset (TRY 2010, region 5)

    Returns
    -------
    tuple_rad : tuple (of arrays)
        Tuple holding direct and diffuse radiation arrays
        (q_direct, q_diffuse) in W/m^2
    """

    try_dat = load_try_data(path_try=path_try)

    (q_direct, q_diffuse) = get_rad_from_try_data(try_data=try_dat)

    return (q_direct, q_diffuse)


if __name__ == '__main__':
    try_dat = load_try_data()

    (q_dir, q_diff) = get_rad_from_try_data(try_data=try_dat)

    import matplotlib.pyplot as plt

    plt.plot(q_dir + q_diff)
    plt.xlabel('Timestep in hours')
    plt.ylabel('Direct and diffuse radiation in W/m^2')
    plt.show()
    plt.close()
