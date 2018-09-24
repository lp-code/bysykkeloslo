# -*- coding: utf-8 -*-

import logging
import os
import pandas as pd
from pathlib import Path
import sys

import bysykkel_data
import calendar_interim
import met_interim
import sun_interim

project_dir = os.sep.join([os.getcwd(), '..', '..'])
sys.path.append(os.sep.join([project_dir, 'src']))
import bysykkel_parameters

def main(input_dir, output_dir, process_bike_data,
         create_calendar, process_met_data):
    """ Runs data processing scripts to process raw data and save it in suitable
        format into data/interim.
        That data is read again by the feature engineering script.
    """
    logger = logging.getLogger(__name__)
    
    if process_bike_data:
        logger.info('Making the interim trip data set from raw data.')

        df = bysykkel_data.read_trip_data(input_dir)
        df = bysykkel_data.augment_trip_data(df) # computes duration
        df = bysykkel_data.remove_invalid_trips(
            df, bysykkel_parameters.max_trip_duration_seconds)
        df.sort_values(by='Start time', inplace=True)
    
        df.reset_index(inplace=True) # without this feather gives an error
        logger.info('Write dataframe to interim, %d lines.' % (len(df.index)))
        df.to_feather(os.sep.join([output_dir, 'trips.feather']))
        df.to_csv(os.sep.join([output_dir, 'trips.csv']), compression='zip')

    if create_calendar: # need datetime for interim met df
        logger.info('Create datetime dataframe.')
        df_date = calendar_interim.create_calendar_df(
            bysykkel_parameters.service_season,
            bysykkel_parameters.summertime_season,
            bysykkel_parameters.time_delta_minutes)
        logger.info('Write datetime info to interim, %d lines.')
        # df_date.to_feather(os.sep.join([output_dir, 'days.feather']))
        df_date.to_csv(os.sep.join([output_dir, 'days.csv']), index=False)

    if process_met_data: # includes the solar elevation
        logger.info('Get met data from raw.')
        df_met = pd.read_feather(os.sep.join([input_dir,
                                              'blindern_met.feather']))
        df_date = pd.read_csv(os.sep.join([output_dir, # from interim!!!
                                           'days.csv']),
                              parse_dates=[0], infer_datetime_format=True)
        df_date['DateTime'] = df_date['DateTime'].dt.tz_localize('UTC')

        # Compute the solar elevation per hour; interpolate in fill_met_data.
        df_met = sun_interim.create_solar_elevation_column(df_met)

        logger.info('Running met_interim.fill_met_data.')
        df_met = met_interim.fill_met_data(
            df_met, df_date, bysykkel_parameters.time_delta_minutes)
        logger.info('Running met_interim.transform_variables.')
        df_met = met_interim.transform_variables(df_met)

        if False:
            df_met = met_interim.sun_below_horizon(df_met)

        df_met.to_csv(os.sep.join([output_dir, 'blindern_interim.csv']),
                      index=False)
        df_met.to_feather(os.sep.join([output_dir, 'blindern_interim.feather']))
        logger.info('Done writing met data interim file.')

if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    raw_data_path = os.sep.join([str(project_dir), 'data', 'raw'])
    interim_data_path = os.sep.join([str(project_dir), 'data', 'interim'])

    main(raw_data_path, interim_data_path,
         process_bike_data=False,
         create_calendar=True,
         process_met_data=True)
