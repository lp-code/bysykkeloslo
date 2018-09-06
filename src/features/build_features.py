# -*- coding: utf-8 -*-

import logging
from pathlib import Path

import os
import pandas as pd


def met_load_data(from_dir):
    return pd.read_feather(os.sep.join([from_dir, 'blindern_met.feather']))


def met_rename_columns(df):
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


def met_transform_wind_direction(df):
    # categories returned: 0 = symmetric around North (0 degrees), otherwise
    # rising towards bigger angles; range = [0, nr_of_categories-1]
    nr_of_categories = 8
    degrees_per_cat = 360. / nr_of_categories
    df['wind_direction_cat'] = df.wind_direction.apply(
            lambda phi: int((phi + degrees_per_cat / 2.) / degrees_per_cat) % nr_of_categories)
    df['wind_direction_cat'].astype('category')
    return df






def load_trip_data(from_dir):
    return pd.read_feather(os.sep.join([from_dir, 'trips.feather']))



def main(input_filepath, output_filepath):
    """ Runs data processing scripts to read interim data from (../interim),
        
        from the internet, and save it in suitable format into data/interim.
        That data is read again by the featuer engineering script.
    """
    logger = logging.getLogger(__name__)
    logger.info('Making the final feature data set from interim data.')

    logger.info('Meteorological data')
    df_met = met_load_data(input_filepath)
    df_met = met_rename_columns(df_met)


    df.reset_index(inplace=True) # without this feather gives an error

    logger.info('Making the interim weather data set from raw data')
    

if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    interim_data_path = os.sep.join([str(project_dir), 'data', 'interim'])
    processed_data_path = os.sep.join([str(project_dir), 'data', 'processed'])

    main(interim_data_path, processed_data_path)

