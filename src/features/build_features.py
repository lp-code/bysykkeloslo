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


def calculate_elevation(tt, loc):
    sun_time = Time(tt)
    if ( (tt.hour == 0) and (tt.minute == 0) ):
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
    for tt in df_times:

        elev = calculate_elevation(tt,loc)
        elev_cat = elevation_to_category(elev,degrees_per_cat,nr_of_categories)
        df_elev.append(elev)
        df_elev_cat.append(elev_cat)

    # df_elev = df_times.apply(calculate_elevation,args=(loc))
    df['solar_elevation_angle'] = pd.DataFrame(df_elev)
    df['solar_elevation_angle'].astype('category')
    df['solar_elevation_cat'] = pd.DataFrame(df_elev_cat)
    df['solar_elevation_cat'].astype('category')

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

    if process_trip_data:
        logger.info('Bicycle data, net demand: start')
        net_demand.compute_net_flow(input_filepath, output_filepath)
        logger.info('Bicycle data, net demand: done')

if __name__ == '__main__':
    log_fmt = '%(asctime)s: , # %(name)s: , # %(levelname)s: , # %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    interim_data_path = os.sep.join([str(project_dir), 'data', 'interim'])
    processed_data_path = os.sep.join([str(project_dir), 'data', 'processed'])

    main(interim_data_path, processed_data_path,
         process_met_data=True, process_trip_data=False)

