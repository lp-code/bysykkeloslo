import datetime
import numpy as np
import os
import pandas as pd
import pprint
import re
import sys
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# modelling stuff
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import make_scorer
from sklearn.metrics import mean_squared_error


def error_func(*args):
    r = np.sqrt(mean_squared_error(*args))
    #print('RMSE: %9.3f' % (r))
    return r


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

param_grid = [
    {
        'n_estimators': range(5, 31, 5),
        'min_samples_split': [0.001, 0.01, 0.1],
        'min_samples_leaf': [0.001, 0.01, 0.1],
        'max_depth': range(3, 15, 2),
        #'max_features': [None]
    }]

regr_model = {}
for station in result_vars[200:201]:
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

    clf = GridSearchCV(RandomForestRegressor(random_state=42, n_jobs=-1),
                       param_grid, cv=5,
                       scoring=make_scorer(error_func,
                                           greater_is_better=False))

    clf.fit(X_train, y_train)

print("Best parameters set found on development set:")
print()
print(clf.best_params_)
print()
print("Grid scores on development set:")
print()
means = clf.cv_results_['mean_test_score']
stds = clf.cv_results_['std_test_score']
for mean, std, params in zip(means, stds, clf.cv_results_['params']):
    print("%0.3f (+/-%0.03f) for %r"
          % (mean, std * 2, params))
print()



"""
    y_test_pred = regr.predict(X_test)
    y_train_pred = regr.predict(X_train)
    nf_0 = np.zeros((len(y_test), 1)) # net flow is zero (state persistence)
    nf_y = [df.loc[first_use_index+i-18, station]
            if first_use_index+i-18 >= 0 else 0
            for i in idx_test] # yesterday's net flow at same time of day

    # Keep some data regarding the model for statistics; currently we also
    # save the regressor objects, while they are saved to the models dir, too.
    regr_model[station] = {
        'rmse_trn': np.sqrt(mean_squared_error(y_train, y_train_pred)),
        'rmse_tst': np.sqrt(mean_squared_error(y_test, y_test_pred)),
        'rmse_p': np.sqrt(mean_squared_error(y_test, nf_0)),
        'rmse_r': np.sqrt(mean_squared_error(y_test, nf_y)),
        'lenXtrain': len(X_train),
        'first_used': station_first_used,
       }
    if write_model_file:
        joblib.dump(regr, os.sep.join([model_dir,
                                       'rf50_'+str(station)+'.joblib']))


pprint.pprint(regr_model)

df_stats = pd.DataFrame.from_dict(data=regr_model,
                                  orient='index',
                                  columns=['first_used', 'lenXtrain',
                                           'rmse_trn', 'rmse_tst',
                                           'rmse_p', 'rmse_r'])
df_stats.to_csv(os.sep.join([model_dir, 'rf50_stats.csv']))
print(df_stats.describe())
"""