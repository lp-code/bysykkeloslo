# -*- coding: utf-8 -*-

# Based on the Jupyter notebook 4_LP_joinDatasets.ipynb

import datetime
import logging
import numpy as np
import os
import pandas as pd
from pathlib import Path
import sys



def join_dataframes(project_dir):
    """ comment
    """
    logger = logging.getLogger(__name__)
    logger.info('Read data sets from processed-directory.')

    processed_data_dir = os.sep.join([project_dir, 'data', 'processed'])
    
    df_date = pd.read_feather(os.sep.join([processed_data_dir,
                                           'datetime_features.feather']))
    df_met  = pd.read_feather(os.sep.join([processed_data_dir,
                                           'blindern_met_features.feather']))
    df_sun  = pd.read_feather(os.sep.join([processed_data_dir,
                                           'solar_elevation_1h.feather']))
    #df_nd   = pd.read_csv(os.sep.join([processed_data_dir, 'net_flow_2016', 'net_flow_05_2016.csv']), parse_dates=[0], infer_datetime_format=True)  # STEPHANIE'S DATA
    #df_nd['Unnamed: 0'] = df_nd['Unnamed: 0'].dt.tz_localize('UTC')
    df_nd = pd.read_feather(os.sep.join([processed_data_dir,
                                         'net_flow.feather']))
    
    logger.info('Join the data sets.')
    # 1)
    df_joined = pd.merge(df_date, df_met,
                         left_on='DateTime', right_on='DateTime', how='left')
    df_joined.drop(columns=['index'], inplace=True)
    # 2)
    df_joined = pd.merge(df_joined, df_sun,
                         left_on='DateTime', right_on='index', how='left')
    df_joined.drop(columns=['index', 'solar_elevation_cat'], inplace=True)
    df_joined['solar_elevation_angle'].interpolate(method='linear',
                                                   inplace=True)
    # 3)
    df_joined = pd.merge(df_joined, df_nd,
                         left_on='DateTime', right_on='index',
                         how='right') # net demand data is leading for join
    
    
    all_vars = df_joined.columns
    cont_vars = ['DateTime', 'temperature', 'wind_speed', 'humidity',
                 'sunshine', 'precipitation', 'solar_elevation_angle']
    cat_vars = [var for var in all_vars if not var in cont_vars]
    logger.info('Variables to be left as-is (cont): %s' % (str(cont_vars)))
    logger.info('Variables to be converted to cat : %s' % (str(cat_vars)))

    # OBS: DETTE GJELDER KUN ENTEN VINTER- ELLER SOMMERTID!!!    
    df_joined = df_joined[(df_joined['index'].dt.hour >= 4) & 
                          (df_joined['index'].dt.hour <  22)]
    
    df_joined = df_joined[((df_joined['index'] >= start16) &
                           (df_joined['index'] <=   end16) ) |
                          ((df_joined['index'] >= start17) &
                           (df_joined['index'] <=   end17) ) |
                          ((df_joined['index'] >= start18) &
                           (df_joined['index'] <=   end18) )]
    
    return df_joined


if __name__ == '__main__':
    log_fmt = '%(asctime)s: , # %(name)s: , # %(levelname)s: , # %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = str(Path(__file__).resolve().parents[2])

    df = join_dataframes(project_dir)
    
    print(len(df.index))
    print(df.isna().sum())
