import glob
import logging
import os
import pandas as pd

def read_trip_data(data_dir):
    '''Read the downloaded monthly csv.gz files and do simple processing of
       the data (remove clearly wrong entries, sort).'''
    trip_files = glob.glob(data_dir + os.sep + 'trips*.csv.zip')
    logger = logging.getLogger(__name__)
    logger.info('Raw data files: %s' % (str(trip_files)))
    df_list = []
    for trip_file in trip_files:
        logger.info('Reading: %s' % (trip_file))
        df_list.append(pd.read_csv(trip_file, compression='zip',
                                   parse_dates=[1, 3],
                                   infer_datetime_format=True))

    logger.info('Done reading data from raw files.')
    df = pd.concat(df_list, ignore_index=True)
    return df


def augment_trip_data(df):
    df['Duration'] = df['End time'] - df['Start time']
    df['DurationSeconds'] = df['Duration'].dt.total_seconds()
    df.drop(['Duration'], axis=1, inplace=True) # data type not supported by
                                                # feather
    return df


def remove_invalid_trips(df, max_trip_duration):
    df = df[(df.DurationSeconds >= 0)&(df.DurationSeconds < max_trip_duration)]

    return df


if __name__ == '__main__':
    print('Module only.')