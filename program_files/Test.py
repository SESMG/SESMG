# -*- coding: utf-8 -*-
"""
Created on Wed Jan 22 12:41:41 2020

@author: Christian
"""
import pvlib
from pvlib.pvsystem import PVSystem
from pvlib.location import Location
from pvlib.modelchain import ModelChain
from pvlib.tools import cosd
import feedinlib.weather as weather
import feedinlib
import matplotlib.pyplot as plt

import pandas as pd
import os

from feedinlib.powerplants import Photovoltaic



data_height = {
    'pressure': 0,
    'temperature': 2,
    'wind_speed': 10,
    'roughness_length': 0}

#pv_system = Photovoltaic(**pv_module)
#weather_df = ready_example_data(os.path.join(os.path.dirname(__file__))+'/interim_data/weather_data.csv')
# set up weather dataframe for pvlib
weather_df_pv = pd.read_csv(
    os.path.join(os.path.dirname(__file__))+'/interim_data/weather_data.csv', index_col=0,
    date_parser=lambda idx: pd.to_datetime(idx, utc=True))
# change type of index to datetime and set time zone
#weather_df_pv.index = pd.to_datetime(weather_df_pv.index).tz_convert(
#    'Europe/Berlin')
weather_df_pv.rename(columns={'temperature': 'temp_air'}, inplace=True)
#weather_df_pv['temp_air'] = weather_df_pv.temp_air - 273.15
weather_df_pv['ghi'] = weather_df_pv.dirhi + weather_df_pv.dhi
weather_df_pv.rename(columns={'windspeed': 'wind_speed'}, inplace=True)

# ######## Pvlib model #########

# specify pv system
yingli210 = {
    'module_name': 'Yingli_YL210__2008__E__',
    'inverter_name': 'ABB__PVI_3_0_OUTD_S_US_Z__277V__277V__CEC_2018_',
    'azimuth': 180,
    'tilt': 30,
    'albedo': 0.2,
    'modules_per_string': 4}

# instantiate feedinlib Photovoltaic object
yingli_module = Photovoltaic(**yingli210)


# calculate feedin
#feedin = yingli_module.feedin(
#                        weather=weather_df_pv[['wind_speed', 'temp_air', 'dhi', 'ghi']],
#                        #location=(52, 13), 
#                        scaling='peak_power', 
#                        scaling_value=10)





my_weather = weather.FeedinWeather(
    data=weather_df_pv,
    timezone='Europe/Berlin',
    latitude=52,
    longitude=13,
    data_height=data_height)

pv_feedin1 = yingli_module.feedin(weather=my_weather,
                                  #location=(52, 13)
                                  )




# plot
feedin.fillna(0).plot(title='PV feedin')
plt.xlabel('Time')
plt.ylabel('Power in W')
plt.show()