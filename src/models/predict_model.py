import datetime
import numpy as np
import os
import pandas as pd
import pprint
import re
import seaborn as sns
import sys
import tqdm

# modelling stuff
from sklearn.ensemble import RandomForestRegressor
from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.externals import joblib

write_model_file = False # True

project_dir = os.sep.join([os.getcwd(), '..', '..'])
processed_data_dir = os.sep.join([project_dir, 'data', 'processed'])
model_dir = os.sep.join([project_dir, 'models', 'RF'])

df = pd.read_feather(os.sep.join([processed_data_dir, 'obs_netflow.feather']))

df_first_use = pd.read_csv(os.sep.join([processed_data_dir, 'stations.csv']),
                        parse_dates=[1], infer_datetime_format=True)
df_first_use.columns = ['station_id', 'first_use']
df_first_use.first_use = df_first_use.first_use.dt.tz_localize('UTC')

cat_vars = {'hour', 'weekday', 'month', 'public_holiday', 'school_holiday',
            'wind_direction_cat', 'weather_fair/cloudy', 'weather_fog/haze',
            'weather_thunderstorm', 'weather_rain', 'weather_snow',
            'weather_other'}
contin_vars = {'temperature', 'wind_speed', 'humidity', 'sunshine',
               'precipitation', 'solar_elevation_angle'}
result_vars = [var for var in df.columns
               if re.fullmatch('[1-9][0-9]+', var)]
# Based on SR's analysis exclude the following variables:
no_correlation_vars = {'wind_direction_cat', 'weather_other',
                       'weather_thunderstorm'}

for v in cat_vars:
    df[v] = df[v].astype('category').cat.as_ordered()
    # @todo Are all "ordered"? Check whether it changes the model if not.

regr_model = {}
feature_importances = []
for station in tqdm.tqdm(result_vars):
    station_first_used = df_first_use.loc[
        df_first_use.station_id == int(station)]['first_use'][0]

    mask = df.DateTime > station_first_used # series, true when station in use
    first_use_index = mask.idxmax()
    nr_lines_for_station = mask.sum()
    indices = range(nr_lines_for_station)

    X_train, X_test, y_train, y_test, idx_train, idx_test = train_test_split(
        df.loc[mask, (cat_vars | contin_vars) - no_correlation_vars],
        df.loc[mask, station],
        indices, test_size=0.3, random_state=42)

    # fit a model (one per station)
    regr = RandomForestRegressor(
        max_depth=7, min_samples_leaf=0.001, min_samples_split=0.001, n_estimators=30,
        random_state=42,
        n_jobs=-1)
    regr.fit(X_train, y_train)
    y_test_pred = regr.predict(X_test)
    y_train_pred = regr.predict(X_train)
    nf_0 = np.zeros((len(y_test), 1)) # net flow is zero (state persistence)
    nf_y = [df.loc[first_use_index+i-18, station]
            if first_use_index+i-18 >= 0 else 0
            for i in idx_test] # yesterday's net flow at same time of day

    # Keep some data regarding the model for statistics; currently we also
    # save the regressor objects, while they are saved to the models dir, too.
    regr_model[station] = {
        'rmse_train': np.sqrt(mean_squared_error(y_train, y_train_pred)),
        'rmse_test': np.sqrt(mean_squared_error(y_test, y_test_pred)),
        'rmse_zero_nf': np.sqrt(mean_squared_error(y_test, nf_0)),
        'rmse_yesterday': np.sqrt(mean_squared_error(y_test, nf_y)),
        'lenXtrain': len(X_train),
        'first_used': station_first_used,
       }
    if write_model_file:
        joblib.dump(regr, os.sep.join([model_dir,
                                       'rf50_'+str(station)+'.joblib']))

    feature_importances.append(dict(zip(X_train.columns,
                                        regr.feature_importances_)))
                                            

df_fi = pd.DataFrame(feature_importances)
df_fi.to_feather('feature_importances.feather')

df_stats = pd.DataFrame.from_dict(data=regr_model,
                                  orient='index',
                                  columns=['first_used', 'lenXtrain',
                                           'rmse_train', 'rmse_test',
                                           'rmse_zero_nf', 'rmse_yesterday'])
df_stats.to_csv(os.sep.join([model_dir, 'rf50_stats.csv']))
print(df_stats.describe())
