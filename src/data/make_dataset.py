# -*- coding: utf-8 -*-
#import click
import logging
from pathlib import Path
#from dotenv import find_dotenv, load_dotenv

import os
import bysykkel_data

#@click.command()
#@click.argument('input_filepath', type=click.Path(exists=True))
#@click.argument('output_filepath', type=click.Path())
def main(input_filepath, output_filepath):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger(__name__)
    logger.info('making final data set from raw data')

    max_trip_duration = 7200
    df = bysykkel_data.read_trip_data(input_filepath)
    df = bysykkel_data.augment_trip_data(df)
    df = bysykkel_data.remove_invalid_trips(df, max_trip_duration)
    print(df.head())
    df.reset_index(inplace=True)
    print(df.head())
    df.to_feather(os.sep.join([output_filepath, 'trips.feather']))
    

if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    #load_dotenv(find_dotenv())

    raw_data_path = os.sep.join(['..', '..', 'data', 'raw'])
    interim_data_path = os.sep.join(['..', '..', 'data', 'interim'])
    if not os.path.exists(raw_data_path):
        raw_data_path = raw_data_path[6:]
        interim_data_path = interim_data_path[6:]

    print(raw_data_path, interim_data_path)
    main(raw_data_path, interim_data_path)
