# -*- coding: utf-8 -*-
#import click
import logging
from pathlib import Path

import os
import bysykkel_data
import met_data

def main(input_filepath, output_filepath):
    """ Runs data processing scripts to read raw data from (../raw), or get it
        from the internet, and save it in suitable format into data/interim.
        That data is read again by the featuer engineering script.
    """
    logger = logging.getLogger(__name__)
    logger.info('Making the interim trip data set from raw data')

    max_trip_duration = 14400
    df = bysykkel_data.read_trip_data(input_filepath)
    df = bysykkel_data.augment_trip_data(df)
    df = bysykkel_data.remove_invalid_trips(df, max_trip_duration)
    df.sort_values(by='Start time', inplace=True)

    df.reset_index(inplace=True) # without this feather gives an error
    logger.info('Write dataframe to feather format.')
    df.to_feather(os.sep.join([output_filepath, 'trips.feather']))
    #logger.info('Write dataframe to csv (zipped).')
    #df.to_csv(os.sep.join([output_filepath, 'trips.csv']),
    #          compression='zip')
    
    if False:
        logger.info('Making the interim weather data set from raw data')
        met_data.get_met_data(output_filepath)
    

if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    raw_data_path = os.sep.join([str(project_dir), 'data', 'raw'])
    interim_data_path = os.sep.join([str(project_dir), 'data', 'interim'])

    print(raw_data_path, interim_data_path)
    main(raw_data_path, interim_data_path)
