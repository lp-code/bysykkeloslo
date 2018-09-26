import datetime
import os
import pandas as pd
import pickle

def find_first_occurence(df, col_station, station_id, col_time):
    df_station = df[df[col_station] == station_id]
    first_time = datetime.datetime(2100, 1, 1) # never smaller than a real data
    if not df_station.empty:
        first_time = df_station.iloc[0][col_time]
    return first_time


df_trips = pd.read_feather(os.sep.join(['..', '..', 'data', 'interim',
                                        'trips.feather']))
df_trips.dropna(axis=0, inplace=True) # drop lines with missing data, <<1%

station_ids_set = set(df_trips['Start station']) | set(df_trips['End station'])


first_use = {
    int(id): min(find_first_occurence(df_trips, 'Start station', id, 'Start time'),
                 find_first_occurence(df_trips, 'End station', id, 'End time'))
    # one of the two is always nondefault
    for id in station_ids_set}

df = pd.DataFrame.from_dict(first_use, orient='index',
                            columns=['first use'])
df.to_csv(os.sep.join(['..', '..', 'data', 'processed', 'stations.csv']))

print('Done.')
