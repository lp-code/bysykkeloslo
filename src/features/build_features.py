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

