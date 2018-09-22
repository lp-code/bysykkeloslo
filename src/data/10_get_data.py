# -*- coding: utf-8 -*-
import logging
import os
import sys
from pathlib import Path

project_dir = os.sep.join([os.getcwd(), '..', '..'])
sys.path.append(os.sep.join([project_dir, 'src']))
from bysykkel_parameters import service_season
import met_data

def main(output_filepath, get_met_data=False):
    """ Get data for the project.
        1) The bike trip data you have to download manually from
           https://developer.oslobysykkel.no/data
        2) The meteorological data is received from the Norwegian met office's
           frost API.
    """
    logger = logging.getLogger(__name__)
    
    if get_met_data:
        logger.info('Get met data from frost & write raw file.')
        met_data.get_met_data(season, output_filepath)
        logger.info('Done writing raw met data file.')

if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]
    raw_data_path = os.sep.join([str(project_dir), 'data', 'raw'])

    main(raw_data_path, get_met_data=True)
