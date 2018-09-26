import logging
import os
import pandas as pd
from pathlib import Path
from shutil import copy2
import sys

project_dir = os.sep.join([os.getcwd(), '..', '..'])
sys.path.append(os.sep.join([project_dir, 'src']))
import bysykkel_parameters

import net_flow

def main(input_dir, output_dir):
    """ Process trip data to net flow and join with day/met/solar data."""
    logger = logging.getLogger(__name__)
    logger.info('Read interim data.')

    # The following data set has the calendar data, along with met and solar
    # elevation.
    df_met = pd.read_feather(os.sep.join([input_dir,
                                          'blindern_interim.feather']))

    logger.info('Bicycle data, compute net flow.')
    df_nf = net_flow.compute_net_flow(input_dir,
                                      bysykkel_parameters.service_season,
                                      bysykkel_parameters.time_delta_minutes)
    logger.info('Bicycle data, net flow done.' + os.linesep + 'Join datasets.')

    df_joined = pd.merge(df_met, df_nf, left_on='DateTime', right_on='index',
                         how='left')
    df_joined.drop(columns=['index'], inplace=True)

    df_joined.to_csv(os.sep.join([output_dir, 'obs_netflow.csv']),
                     index=False)
    df_joined.to_feather(os.sep.join([output_dir, 'obs_netflow.feather']))


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    interim_data_path = os.sep.join([str(project_dir), 'data', 'interim'])
    processed_data_path = os.sep.join([str(project_dir), 'data', 'processed'])

    main(interim_data_path, processed_data_path)
