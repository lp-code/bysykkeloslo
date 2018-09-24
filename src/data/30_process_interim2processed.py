import logging
import os
from pathlib import Path
from shutil import copy2

#import net_flow

def main(input_dir, output_dir):
    logger = logging.getLogger(__name__)
    logger.info('Process interim data.')
    copy2(os.sep.join([input_dir, 'blindern_interim.feather']),
          os.sep.join([output_dir, 'days_met_sun.feather']))
    #copy2(os.sep.join([input_dir, 'blindern_interim.feather']),
    #      os.sep.join([output_dir, 'days_met_sun.feather']))


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    interim_data_path = os.sep.join([str(project_dir), 'data', 'interim'])
    processed_data_path = os.sep.join([str(project_dir), 'data', 'processed'])

    main(interim_data_path, processed_data_path)
