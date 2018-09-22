# -*- coding: utf-8 -*-

import logging
from pathlib import Path

import os
import bysykkel_data
import met_data
import os
project_dir = os.sep.join([os.getcwd(), '..', '..'])
sys.path.append(os.sep.join([project_dir, 'src']))
from bysykkel_parameters import max_trip_duration_seconds

def main(input_filepath, output_filepath,
         process_bike_data=False, process_met_data=False):
    """ Runs data processing scripts to process raw data and save it in suitable
        format into data/interim.
        That data is read again by the feature engineering script.
    """
    logger = logging.getLogger(__name__)
    
    if process_bike_data:
        logger.info('Making the interim trip data set from raw data.')

        df = bysykkel_data.read_trip_data(input_filepath)
        df = bysykkel_data.augment_trip_data(df)
        df = bysykkel_data.remove_invalid_trips(df, max_trip_duration_seconds)
        df.sort_values(by='Start time', inplace=True)
    
        df.reset_index(inplace=True) # without this feather gives an error
        logger.info('Write dataframe to feather format.')
        df.to_feather(os.sep.join([output_filepath, 'trips.feather']))
        df.to_csv(os.sep.join([output_filepath, 'trips.csv']), compression='zip')
    
    if process_met_data:
        logger.info('Get met data from frost & write interim file.')
        met_data.get_met_data(output_filepath)
        logger.info('Done writing met data interim file.')

if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    raw_data_path = os.sep.join([str(project_dir), 'data', 'raw'])
    interim_data_path = os.sep.join([str(project_dir), 'data', 'interim'])

    main(raw_data_path, interim_data_path,
         process_bike_data=False, process_met_data=False)
