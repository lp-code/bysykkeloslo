# -*- coding: utf-8 -*-

import logging
import numpy as np
import astropy.coordinates as coord
from astropy.time import Time
import time, datetime
from datetime import datetime, timedelta
import net_demand
import os
import pandas as pd
from pathlib import Path


def met_load_data(from_dir):
    return pd.read_feather(os.sep.join([from_dir, 'blindern_met.feather']))


def met_write_data(df, to_dir):
    return df.to_feather(os.sep.join([to_dir,
                                         'blindern_met_features.feather']))

    
def met_rename_columns(df):
    '''Assign shorter, easy-to-understand column names.'''
    
    df.rename(columns = {
            'air_temperature': 'temperature',
            'max(wind_speed PT1H)': 'wind_speed',
            'max_wind_speed(wind_from_direction PT1H)': 'wind_direction',
            'relative_humidity': 'humidity',
            'sum(duration_of_sunshine PT1H)': 'sunshine',
            'weather_type' : 'weather1',
            'over_time(weather_type_primary_significance PT6H)': 'weather2',
            'over_time(weather_type_secondary_significance PT6H)': 'weather3',
            'sum(precipitation_amount PT1H)': 'precipitation',
            }, inplace=True)
    return df


def met_transform_wind_direction(df, delete_original=True):
    '''Transform wind direction in degrees to categories
    categories returned: 0 = symmetric around North (0 degrees), otherwise
    rising towards bigger angles; range = [0, nr_of_categories-1].'''
    nr_of_categories = 8
    degrees_per_cat = 360. / nr_of_categories
    df['wind_direction_cat'] = df.wind_direction.apply(
            lambda phi: int((phi + degrees_per_cat / 2.) / degrees_per_cat) % nr_of_categories)
    df['wind_direction_cat'].astype('category')
    if delete_original:
        df.drop(columns='wind_direction', inplace=True)
    return df

def calculate_elevation(time,loc):
    sun_time = Time(time)
    if ( (time.hour == 0) and (time.minute == 0) ):
        print(f'Calculate solar elevation angle for: {time}')
    zen_ang = coord.get_sun(sun_time).transform_to(coord.AltAz(obstime=sun_time, location=loc)).alt.degree
    return zen_ang

def elevation_to_category(solar_elevation,degrees_per_cat,nr_of_categories):
    upper = 0.
    for icategory in range(nr_of_categories):
        if (solar_elevation < upper):
            return icategory
        upper += degrees_per_cat
    return nr_of_categories

def insert_timesteps(df,timestepinterval):
    dfarray = df.values
    dflist = []
    for dfline in dfarray:
        totalinterval=0
        while (totalinterval < 60):
            dflist.append(dfline)
            dfline = dfline + timedelta(minutes = timestepinterval)
            totalinterval += timestepinterval
    dfarray = np.asarray(dflist)
    newdf = pd.DataFrame({'index':dfarray})
    return newdf

def elev_calculate_elevation(df, df_times,loc):
    '''Calculate solar elevation angle in degrees above horizon
    based on time and location'''

    nr_of_categories = 15
    degrees_per_cat = 90. / nr_of_categories

    df_elev = []
    df_elev_cat = []
    for time in df_times:

        elev = calculate_elevation(time,loc)
        elev_cat = elevation_to_category(elev,degrees_per_cat,nr_of_categories)
        df_elev.append(elev)
        df_elev_cat.append(elev_cat)

    # df_elev = df_times.apply(calculate_elevation,args=(loc))
    df['solar_elevation_angle'] = pd.DataFrame(df_elev)
    df['solar_elevation_angle'].astype('category')
    df['solar_elevation_cat'] = pd.DataFrame(df_elev_cat)
    df['solar_elevation_cat'].astype('category')

    return df

class WMO4677_translator(object):
    '''
    Translate from the standard codes to a system with just six categories.
    '''
    
    def __init__(self):
        self.__nr_of_categories = 6
        self.__cat_names = [
                'weather_fair/cloudy',  # 0
                'weather_fog/haze',     # , bad visibility: 1
                'weather_thunderstorm', # thunder/lightning: 2
                'weather_rain',         # precipitation/hail: 3
                'weather_snow',         # 4 
                'weather_other',        # 5
                ]
        self.__wc_dict = {
        0: 0, # Cloud development not observed or not observable
        1: 0, # Cloud generally dissolving or becoming less developed
        2: 0, # State of sky on the whole unchanged
        3: 0, # Clouds generally forming or developing
        4: 1, # Visibility reduced by smoke, e.g. veldt or forest fires,
              # industrial smoke or volcanic ashes
        5: 1, # Haze
        6: 1, # Widespread dust in suspension in the air, not raised by wind
              # at or near the station at the time of observation
        7: 1, # Dust or sand raised by wind at or near the station at the time
              # of  observation, but not well-developed dust whirl(s) or sand
              # whirl(s), and no duststorm or sandstorm seen; or, in the case
              # of ships, blowing spray at the station
        8: 1, # Well-developed dust or sand whirl(s) seen at or near the
              # station during the preceding hour or at the time of
              # observation, but no dust storm or sandstorm
        9: 1, # Duststorm or sandstorm within sight at the time of observation,
              # or at the station during the preceding hour
        10: 1, # Mist
        11: 1, # Patches of shallow fog or ice fog at the station, whether on
               # land or sea not deeper than about 2 metres on land or 10
               # metres at sea
        12: 1, # More or less continuous shallow fog or ice fog at the station,
               # whether on land or sea, not deeper than about 2m/land or
               # 10m/sea
        13: 2, # Lightning visible, no thunder heard
        14: 3, # Precipitation within sight, not reaching the ground or the
               # surface of the sea
        15: 3, # Precipitation within sight, reaching the ground or the surface
               # of the sea, but distant, i.e. > 5 km from the station
        16: 3, # Precipitation within sight, reaching the ground or the surface
               # of the sea, near to, but not at the station
        17: 2, # Thunderstorm, but no precipitation at the time of observation
        18: 3, # Squalls at or within sight of the station during the preceding
               # hour or at the time of observation
        19: 5, # Funnel clouds at or within sight of the station during the
               # preceding hour or at the time of observation
        20: 3, # Drizzle (not freezing) or snow grains, not falling as
               # showers, during the preceding hour but not at the time of
               # observation
        21: 3, # Rain (not freezing), not falling as showers, during the
               # preceding hour but not at the time of observation
        22: 4, # Snow, not falling as showers, during the preceding hour but
               # not at the time of observation
        23: 3, # Rain and snow or ice pellets, not falling as showers;
               # during the preceding hour but not at the time of observation
        24: 4, # Freezing drizzle or freezing rain; during the preceding hour
               # but not at the time of observation
        25: 3, # Shower(s) of rain during the preceding hour but not at the
               # time of observation
        26: 4, # Shower(s) of snow, or of rain and snow during the preceding
               # hour but not at the time of observation
        27: 3, # Shower(s) of hail, or of rain and hail during the preceding
               # hour but not at the time of observation
        28: 1, # Fog or ice fog during the preceding hour but not at the
               # time of observation
        29: 2, # Thunderstorm (with or without precipitation) during the
               # preceding hour but not at the time of observation
        30: 1, # Slight or moderate duststorm or sandstorm:
               # has decreased during the preceding hour
        31: 1, # Slight or moderate duststorm or sandstorm:
               # no appreciable change during the preceding hour
        32: 1, # Slight or moderate duststorm or sandstorm:
               # has begun or has increased during the preceding hour
        33: 1, # Severe duststorm or sandstorm:
               # has decreased during the preceding hour
        34: 1, # Severe duststorm or sandstorm:
               # no appreciable change during the preceding hour
        35: 1, # Severe duststorm or sandstorm:
               # has begun or has increased during the preceding hour
        36: 4, # Slight/moderate drifting snow:
               # generally low (below eye level)
        37: 4, # Heavy drifting snow: generally low (below eye level)
        38: 4, # Slight/moderate blowing snow: generally high (above eye level)
        39: 4, # Heavy blowing snow: generally high (above eye level)
        40: 1, # Fog or ice fog at a a distance at the time of observation,
               # but not at station during the preceding hour, the fog or
               # ice fog extending to a level above that of  the observer
        41: 1, # Fog or ice fog in patches
        42: 1, # Fog/ice fog, sky visible, has become thinner during the
               # preceding hour
        43: 1, # Fog/ice fog, sky invisible, has become thinner during the
               # preceding hour
        44: 1, # Fog or ice fog, sky visible, no appreciable change during the
               # past hour
        45: 1, # Fog or ice fog, sky invisible, no appreciable change during
               # the preceding hour
        46: 1, # Fog or ice fog, sky visible, has begun or has become thicker
               # during preceding hour
        47: 1, # Fog or ice fog, sky invisible, has begun or has become
               # thicker during the preceding hour
        48: 1, # Fog, depositing rime, sky visible
        49: 1, # Fog, depositing rime, sky invisible
        50: 3, # Drizzle, not freezing, intermittent, slight at time of ob.
        51: 3, # Drizzle, not freezing, continuous, slight at time of ob.
        52: 3, # Drizzle, not freezing, intermittent, moderate at time of ob.
        53: 3, # Drizzle, not freezing, continuous, moderate at time of ob.
        54: 3, # Drizzle, not freezing, intermittent, heavy at time of ob.
        55: 3, # Drizzle, not freezing, continuous, heavy at time of ob.
        56: 3, # Drizzle, freezing, slight
        57: 3, # Drizzle, freezing, moderate or heavy (dense)
        58: 3, # Rain and drizzle, slight
        59: 3, # Rain and drizzle, moderate or heavy
        60: 3, # Rain, not freezing, intermittent, slight at time of ob.
        61: 3, # Rain, not freezing, continuous, slight at time of ob.
        62: 3, # Rain, not freezing, intermittent, moderate at time of ob.
        63: 3, # Rain, not freezing, continuous, moderate at time of ob.
        64: 3, # Rain, not freezing, intermittent, heavy at time of ob.
        65: 3, # Rain, not freezing, continuous, heavy at time of ob.
        66: 3, # Rain, freezing, slight
        67: 3, # Rain, freezing, moderate or heavy
        68: 3, # Rain or drizzle and snow, slight
        69: 3, # Rain or drizzle and snow, moderate or heavy
        70: 4, # Intermittent fall of snowflakes, slight at time of ob.
        71: 4, # Continuous fall of snowflakes, slight at time of ob.
        72: 4, # Intermittent fall of snowflakes, moderate at time of ob.
        73: 4, # Continuous fall of snowflakes, moderate at time of ob.
        74: 4, # Intermittent fall of snowflakes, heavy at time of ob.
        75: 4, # Continuous fall of snowflakes, heavy at time of ob.
        76: 4, # Diamond dust (with or without fog)
        77: 4, # Snow grains (with or without fog)
        78: 4, # Isolated star-like snow crystals (with or without fog)
        79: 4, # Ice pellets
        80: 3, # Rain shower(s), slight
        81: 3, # Rain shower(s), moderate or heavy
        82: 3, # Rain shower(s), violent
        83: 3, # Shower(s) of rain and snow, slight
        84: 3, # Shower(s) of rain and snow, moderate or heavy
        85: 4, # Snow shower(s), slight
        86: 4, # Snow shower(s), moderate or heavy
        87: 4, # Shower(s) of snow pellets or small hail, with or without
               # rain or rain and snow mixed: , # slight
        88: 4, # Shower(s) of snow pellets or small hail, with or without
               # rain or rain and snow mixed: , # moderate or heavy
        89: 4, # Shower(s) of hail, with or without rain or rain and snow
               # mixed, not associated with thunder: , # slight
        90: 4, # Shower(s) of hail, with or without rain or rain and snow
               # mixed, not associated with thunder: , # moderate or heavy
        91: 2, # Slight rain at time of observation: , # Thunderstorm during
               # the preceding hour but not at time of observation
        92: 2, # Moderate or heavy rain at time of observation:
               # Thunderstorm during the preceding hour but not at time of
               # observation
        93: 2, # Slight snow, or rain and snow mixed or hail at time of
               # observation: Thunderstorm during the preceding hour but not
               # at time of observation
        94: 2, # Moderate or heavy snow, or rain and snow mixed or hail at
               # time of observation: Thunderstorm during the preceding hour
               # but not at time of observation
        95: 2, # Thunderstorm, slight or moderate, without hail, but with
               # rain and/or snow at time of observation
        96: 2, # Thunderstorm, slight or moderate, with hail at time of ob.
        97: 2, # Thunderstorm, heavy, without hail, but with rain and/or
               # snow at time of observation
        98: 2, # Thunderstorm combined with dust/sandstorm at time of
               # observation
        99: 2, # Thunderstorm, heavy with hail at time of observation
        }
    
    
    def met2cat(self, met_code):
        return self.__wc_dict[met_code]
    
    
    def cat_name(self, cat):
        return self.__cat_names[cat]
    

    def nr_of_categories(self):
        return self.__nr_of_categories
    
    

def met_transform_weather(df, delete_original=True):
    '''Observations of the current weather phenomena are given in up to three
    columns at observation times, i.e. every 3rd hour, except at night.
    Transform the numerical codes to a small number of categories, stored
    as 1-hot-encoding. In addition, fill downwards to the following two hours
    after each observation. If all of the categories are zero, then no
    observation was available at the time -- typically this affects night time
    from 21 to 05.'''
    translator = WMO4677_translator()
    
    # create new feature columns
    for ic in range(translator.nr_of_categories()):
        df[translator.cat_name(ic)] = np.nan

    for index, row in df.iterrows():
        for col in ['weather1', 'weather2', 'weather3']:
            if not np.isnan(row[col]):
                met_code = int(row[col])
                cat = translator.met2cat(met_code)
                df.loc[index, translator.cat_name(cat)] = 1
                
    for ic in range(translator.nr_of_categories()):
        # First fill weather columns in 3-hour-packs; this will leave the
        # columns that are not activated by the weather_i fields at the initial
        # value nan. Therefore fill the remaining nans with 0.
        cat_name = translator.cat_name(ic)
        df[cat_name].fillna(method='ffill', limit=2, inplace=True)
        df[cat_name].fillna(value=0, inplace=True)
        df[cat_name] = df[cat_name].astype('int32')

    if delete_original:
        for col in ['weather1', 'weather2', 'weather3']:
            df.drop(columns=col, inplace=True)
    
    return df


def load_trip_data(from_dir):
    return pd.read_feather(os.sep.join([from_dir, 'trips.feather']))



def main(input_filepath, output_filepath,
         process_met_data, process_trip_data):
    """ Runs data processing scripts to read interim data from input_filepath,
        generate features and write to output_filepath.
    """
    logger = logging.getLogger(__name__)
    logger.info('Making the final feature data set from interim data.')

    if process_met_data:
        logger.info('Meteorological data: start')
        df_met = met_load_data(input_filepath)
        df_met = met_rename_columns(df_met)
        df_met = met_transform_wind_direction(df_met)
        df_met = met_transform_weather(df_met)
    
        df_met.reset_index(inplace=True) # without this feather gives an error
        
        met_write_data(df_met, output_filepath)
        logger.info('Meteorological data: done')
    
    if process_trip_data:
        logger.info('Bicycle data, net demand: start')
        net_demand.compute_net_demand(input_filepath, output_filepath)
        logger.info('Bicycle data, net demand: done')

if __name__ == '__main__':
    log_fmt = '%(asctime)s: , # %(name)s: , # %(levelname)s: , # %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    interim_data_path = os.sep.join([str(project_dir), 'data', 'interim'])
    processed_data_path = os.sep.join([str(project_dir), 'data', 'processed'])

    main(interim_data_path, processed_data_path,
         process_met_data=False, process_trip_data=True)

