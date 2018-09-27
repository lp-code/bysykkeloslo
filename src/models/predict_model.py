import datetime
import numpy as np
import os
import pandas as pd
import sys
from pprint import pprint
import re

# modelling stuff
from sklearn.ensemble import RandomForestRegressor
from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error


project_dir = os.sep.join([os.getcwd(), '..', '..'])
processed_data_dir = os.sep.join([project_dir, 'data', 'processed'])

df = pd.read_feather(os.sep.join([processed_data_dir, 'obs_netflow.feather']))

df_first_use = pd.read_csv(os.sep.join([processed_data_dir, 'stations.csv']),
                        parse_dates=[1], infer_datetime_format=True)
df_first_use.columns = ['station_id', 'first_use']
df_first_use.first_use = df_first_use.first_use.dt.tz_localize('UTC')

cat_vars = ['hour', 'weekday', 'month', 'public_holiday', 'school_holiday',
            'wind_direction_cat', 'weather_fair/cloudy', 'weather_fog/haze',
            'weather_thunderstorm', 'weather_rain', 'weather_snow',
            'weather_other']
contin_vars = ['temperature', 'wind_speed', 'humidity', 'sunshine',
               'precipitation', 'solar_elevation_angle']
result_vars = [var for var in df.columns
               if re.fullmatch('[1-9][0-9]+', var)]
for v in cat_vars:
    df[v] = df[v].astype('category').cat.as_ordered()
    # @todo Are all "ordered"? Check whether it changes the model if not.

regr = {}
for station in result_vars:
    station_first_used = df_first_use.loc[
        df_first_use.station_id == int(station)]['first_use'][0]
    X_train, X_test, y_train, y_test = train_test_split(
        df.loc[df.DateTime > station_first_used, cat_vars + contin_vars],
        df.loc[df.DateTime > station_first_used, station],
        test_size=0.3, random_state=42)
    print(f'Station: {station}  first used: {station_first_used}  number of rows: {len(X_train)}')

    # fit a model (one per station)
    regr[station] = RandomForestRegressor(n_estimators=50, random_state=42, n_jobs=-1)
    regr[station].fit(X_train, y_train)
    y_pred = regr[station].predict(X_test)
    print(np.sqrt(mean_squared_error(y_test, y_pred)))
