import pandas as pd
import numpy as np

pd.options.mode.chained_assignment = None

df_test = pd.read_csv('C:\\Users\\anhaug\\Documents\\Hackathon\\trips.csv')

# Sorting the code chronologically in "Start time"
df_test["Start time"] = pd.to_datetime(df_test["Start time"])
df_test = df_test.sort_values(by="Start time")
df_test = df_test.reset_index(drop=True)

# Initializing useful variables
t_start = '2016-04-01 04:00:00'  # must be changed based on the csv-file
t_end = '2018-08-31 22:00:00'  # must be changed based on the csv-file
length_of_csv_file = len(df_test.index)
max_station_number = int(np.maximum(df_test['Start station'].max(), df_test['End station'].max()))
min_station_number = int(np.minimum(df_test['Start station'].min(), df_test['End station'].min()))
no_stations = max_station_number - min_station_number + 1

# initializing net demand DataFrame
bike_station_no = []
for i in range(min_station_number, max_station_number + 1):
    bike_station_no.append(i)

time_steps = pd.date_range(start=t_start, end=t_end, freq='5min')
pd_net_demand = pd.DataFrame(index=time_steps, columns=bike_station_no)

S_start = pd.to_datetime(df_test["Start time"])
S_end = pd.to_datetime(df_test["End time"])

day_counter = 0

# counting the bikes that leave the stations
for i, df_day_split in df_test.groupby([(S_start - pd_net_demand.index[0]).astype('timedelta64[5m]')]):
    df_day_split = df_day_split.reset_index(drop=True)
    new_row = np.zeros(no_stations)
    elements_in_list = len(df_day_split.index)
    for k in range(elements_in_list):
        for j in range(min_station_number, max_station_number + 1):
            counter = 0
            if (df_day_split["Start station"].loc[k] == j):
                counter -= 1
            new_row[j - min_station_number] += counter
    pd_net_demand.iloc[day_counter] = new_row
    day_counter += 1
day_counter = 0

# counting the bikes that enter the stations
for i, df_day_split in df_test.groupby([(S_end - pd_net_demand.index[0]).astype('timedelta64[5m]')]):
    df_day_split = df_day_split.reset_index(drop=True)
    new_row = np.zeros(no_stations)
    elements_in_list = len(df_day_split.index)
    for k in range(elements_in_list):
        for j in range(min_station_number, max_station_number + 1):
            counter = 0
            if (df_day_split["End station"].loc[k] == j):
                counter += 1
            new_row[j - min_station_number] += counter
    pd_net_demand.iloc[day_counter] = pd_net_demand.iloc[day_counter] + new_row
    day_counter += 1
print(pd_net_demand)

pd_net_demand.to_csv('C:\\Users\\anhaug\\Documents\\Hackathon\\net_demand_final.csv')