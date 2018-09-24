import datetime
import os
import pandas as pd
import tqdm


def find_row(t, t0, delta):
    #t0 = t0.replace(tzinfo=None) #datetime.timezone.utc)
    #print(t, t.tzname(), t0, t0.tzname(), delta)
    return int((t - t0) / delta)


def compute_net_flow(input_filepath, seasons, timestep):
    # Read from the interim directory.
    df_trips = pd.read_feather(os.sep.join([input_filepath, 'trips.feather']))
    df_trips.dropna(axis=0, inplace=True) # drop lines with missing data, <<1%

    station_ids_set = set(df_trips['Start station']) | set(
            df_trips['End station'])
    station_ids_list = sorted([str(int(x)) for x in station_ids_set])

    # For the net flow we have to make a time range _without_ the winter/
    # "no season"-gaps, because that makes it easier to find the row number
    # (on the time index) for a given trip.
    years = sorted(seasons.keys())
    delta = datetime.timedelta(minutes=timestep)
    t_start = seasons[years[0]]['start']
    t_end = seasons[years[-1]]['end']
    df_nf = pd.DataFrame(index=pd.date_range(start=t_start,
                                             end=t_end,
                                             freq='%dmin' % timestep,
                                             tz=datetime.timezone.utc),
                         columns=station_ids_list)
    df_nf[:] = 0
    for col in df_nf.columns:
        df_nf[col].astype('int32')

    utc = datetime.timezone.utc
    for i_trip, row in tqdm.tqdm(df_trips.iterrows(),
                                 total=len(df_trips.index)):
        i_start = find_row(row['Start time'].replace(tzinfo=utc), t_start, delta)
        df_nf.iloc[i_start][str(int(row['Start station']))] -= 1 # start
        i_end = find_row(row['End time'].replace(tzinfo=utc), t_start, delta)
        df_nf.iloc[i_end][str(int(row['End station']))] += 1 # trip end

    df_nf.reset_index(inplace=True)
    #df_nf['index'] = df_nf['index'].dt.tz_localize('UTC')

    return df_nf
