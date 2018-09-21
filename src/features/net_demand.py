import datetime
import os
import pandas as pd
import tqdm


def find_row(t, t0, delta):
    return int((t - t0) / delta)


def compute_net_flow(input_filepath, output_filepath, timestep=5):
    # Read from the interim directory.
    df_trips = pd.read_feather(os.sep.join([input_filepath, 'trips.feather']))
    df_trips.dropna(axis=0, inplace=True) # drop lines with missing data, <<1%

    t_start = datetime.datetime(2016,  4,  1,  0,  0,  0, 0)
    t_end   = datetime.datetime(2018,  8, 31, 23, 59, 59, 0)
    delta = datetime.timedelta(minutes=timestep)
    
    station_ids_set = set(df_trips['Start station']) | set(
            df_trips['End station'])
    station_ids_list = sorted([str(int(x)) for x in station_ids_set])

    time_steps = pd.date_range(start=t_start, end=t_end,
                               freq='%dmin' % timestep)
    df_nd = pd.DataFrame(index=time_steps, columns=station_ids_list)
    df_nd[:] = 0
    for col in df_nd.columns:
        df_nd[col].astype('int32')
    
    for i_trip, row in tqdm.tqdm(df_trips.iterrows(),
                                 total=len(df_trips.index)):
        i_slot_start = find_row(row['Start time'], t_start, delta)
        df_nd.iloc[i_slot_start][str(int(row['Start station']))] -= 1 # start
        i_slot_end = find_row(row['End time'], t_start, delta)
        df_nd.iloc[i_slot_end][str(int(row['End station']))] += 1 # trip end

    df_nd.reset_index(inplace=True)
    df_nd['index'] = df_nd['index'].dt.tz_localize('UTC')
    df_nd.to_feather(os.sep.join([output_filepath, 'net_flow.feather']))
    df_nd.to_csv(os.sep.join([output_filepath, 'net_flow.csv']))
    