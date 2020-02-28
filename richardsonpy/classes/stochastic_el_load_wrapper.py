#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 21 14:09:28 2015

@author: tsz
"""
from __future__ import division

import os
import numpy as np
import richardsonpy.classes.lighting as lighting_model
import richardsonpy.classes.appliance as appliance_model


class ElectricityProfile(object):
    """
    ElectricityProfile class
    """

    type_weekday = ["wd", "we"]  # weekday, weekend

    # Load statistics for appliances (transition probability matrix)
    activity_statistics = {}
    activity_statistics_loaded = False

    def __init__(self, appliances, lightbulbs):
        """
        This class loads all input data
        
        Parameters
        ----------
        appliances : list
            List of appliance configurations
        ligthbulbs : list
            List of lightbulb configurations
        """
        src_path = os.path.dirname(os.path.dirname(__file__))
        folder = os.path.join(src_path, 'inputs', 'constants')
        if not ElectricityProfile.activity_statistics_loaded:
            # Load activity statistics
            ElectricityProfile.activity_statistics_loaded = True

            for weekday in self.type_weekday:
                filename = "ActiveAppliances_" + weekday + ".csv"
                file_path = os.path.join(folder, filename)
                temp = (np.loadtxt(file_path, delimiter=";")).tolist()
                ElectricityProfile.activity_statistics[weekday] = temp

        # Create lighting configuration
        self.lighting_config = lighting_model.LightingModelConfiguration()

        # Save inputs
        self.appliances = appliances
        self.lightbulbs = lightbulbs

    def _get_month(self, day, leap_year=False):
        """

        Parameters
        ----------
        day : int
            Day number
        leap_year : bool, optional
            Boolean to define leap year (default: False). If True, uses
            leap year

        Returns
        -------

        """
        if leap_year:
            days = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        else:
            days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

        days_summed = np.cumsum(days)

        for i in range(len(days)):
            if days_summed[i] >= day:
                break
        return int(i + 1)

    def power_sim(self, irradiation, weekend, day, occupancy):
        """
        Calculate electric power for lighting and appliance usage.

        Parameters
        ----------
        irradiation : Array-like
            Solar irradiation on a horizontal plane for one day (1 minute res.)
        weekend : Boolean
            - True: Weekend
            - False: Monday - Friday
        day : Integer
            Day of the (computation) year.
        occupancy : Array-like
            Occupancy for one day (10 minute resolution)

        Returns
        -------
        tup_res : tuple (of arrays)
            Results tuple (power_el_total, power_el_light,
            power_el_app)
            power_el_total : array
                Array holding total el. power values in Watt
            power_el_light : array
                Array holding el. power values for light usage in Watt
            power_el_app : array
                Array holding el. power values for appliance usage in Watt
        """
        month = self._get_month(day)

        # Lighting
        demand_lighting = lighting_model.run_lighting_simulation(
            vOccupancyArray=occupancy,
            vBulbArray=self.lightbulbs,
            vIrradianceArray=irradiation,
            light_mod_config=self.lighting_config)

        # Appliances
        fun = appliance_model.run_application_simulation
        type_weekday = self.type_weekday[weekend]
        activity_statistics = self.activity_statistics[type_weekday]
        demand_appliances = fun(occupancy, self.appliances,
                                activity_statistics, month)

        power_el_light = np.sum(demand_lighting, axis=0)
        power_el_app = np.sum(demand_appliances, axis=0)

        power_el_total = power_el_app + power_el_light

        return (power_el_total, power_el_light, power_el_app)
