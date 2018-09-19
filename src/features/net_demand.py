import datetime
import os
import pandas as pd
import tqdm

pd.options.mode.chained_assignment = None

def find_row(t, t0, delta):
    return int((t - t0) / delta)

def compute_net_demand(input_filepath, output_filepath, timestep=5):
    # Read from the interim directory.
    df_trips = pd.read_feather(os.sep.join([input_filepath, 'trips.feather']))
    df_trips.dropna(axis=0, inplace=True)

    t_start = '2016-04-01 04:00:00'  # must be changed based on the csv-file
    t_end   = '2018-08-31 22:00:00'  # must be changed based on the csv-file
    delta = datetime.timedelta(minutes=timestep)
    t0 = datetime.datetime.strptime(t_start, '%Y-%m-%d %H:%M:%S')
    
    station_ids_set = set(map(str, df_trips['Start station'])) | set(
            map(str, df_trips['End station']))
    station_ids_list = sorted(list(station_ids_set))

    time_steps = pd.date_range(start=t_start, end=t_end,
                               freq='%dmin' % timestep)
    df_nd = pd.DataFrame(index=time_steps, columns=station_ids_list)
    df_nd[:] = 0
    for col in df_nd.columns:
        df_nd[col].astype('int32')
    
    for i_trip, row in tqdm.tqdm(df_trips.iterrows(),
                                 total=len(df_trips.index)):
        i_slot_start = find_row(row['Start time'], t0, delta)
        df_nd.iloc[i_slot_start][str(row['Start station'])] -= 1 # away from start
        i_slot_end = find_row(row['End time'], t0, delta)
        df_nd.iloc[i_slot_end][str(row['End station'])] += 1 # add bike at end

    df_nd.reset_index(inplace=True)
    df_nd.to_feather(os.sep.join([output_filepath, 'net_demand.feather']))
    