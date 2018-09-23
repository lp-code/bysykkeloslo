# -*- coding: utf-8 -*-

import numpy as np
import os
import pandas as pd
from datetime import timezone as tz
from dateutil.tz import tzutc

project_dir = os.sep.join([os.getcwd(), '..'])

_public_holidays = [
    # 2016
    '2016-01-01', # Første nyttårsdag
    '2016-03-24', # Skjærtorsdag
    '2016-03-25', # Langfredag
    '2016-04-27', # Første påskedag
    '2016-04-28', # Andre påskedag
    '2016-05-01', # Arbeidernes dag
    '2016-05-05', # Kristi Himmelfartsdag
    '2016-05-05', # Første pinsedag
    '2016-05-16', # Andre pinsedag
    '2016-05-17', # Grunnlovsdag
    '2016-12-25', # Første juledag
    '2016-12-26', # Andre juledag
    # 2017
    '2017-01-01', # Første nyttårsdag
    '2017-04-13', # Skjærtorsdag
    '2017-04-14', # Langfredag
    '2017-04-16', # Første påskedag
    '2017-04-17', # Andre påskedag
    '2017-05-01', # Arbeidernes dag
    '2017-05-17', # Grunnlovsdag
    '2017-05-25', # Kristi Himmelfartsdag
    '2017-06-04', # Første pinsedag
    '2017-06-05', # Andre pinsedag
    '2017-12-25', # Første juledag
    '2017-12-26', # Andre juledag
    # 2018
    '2018-01-01', # Første nyttårsdag
    '2018-03-29', # Skjærtorsdag
    '2018-03-30', # Langfredag
    '2018-04-01', # Første påskedag
    '2018-04-02', # Andre påskedag
    '2018-05-01', # Arbeidernes dag
    '2018-05-10', # Kristi Himmelfartsdag
    '2018-05-17', # Grunnlovsdag
    '2018-05-20', # Første pinsedag
    '2018-05-21', # Andre pinsedag
    '2018-12-25', # Første juledag
    '2018-12-26', # Andre juledag
    ]
def _is_public_holiday(row):
    for ph in _public_holidays:
        if row['DateTime'].strftime('%Y-%m-%d') == ph:
            return 1
    return 0

_school_holidays = [
    ['2016-02-29', '2016-03-04'], # vinterferie
    ['2016-03-21', '2016-03-29'], # påske+planleggingsdag
    ['2018-06-22', '2016-08-21'], # holiday start uncertain; Skolestart: Mandag 22.08.2016
    ['2016-10-03', '2016-10-07'], # Høstferie
    ['2016-12-22', '2017-01-02'], # Juleferie: F.o.m. torsdag 22.12.2016 t.o.m. mandag 02.01.2017
    ['2017-02-20', '2017-02-24'], # Vinterferie 2017
    ['2017-04-10', '2017-04-17'], # Påskeferie 2017
    ['2017-05-26', '2017-05-26'], # Fridag (inneklemt dag)
    ['2017-06-22', '2017-08-20'], # sommerferien (for vgs)
    ['2017-09-11', '2017-09-11'], # Fri valgdagen: 11. september 2017
    ['2017-10-02', '2017-10-06'], # Høstferien 2017
    ['2017-12-22', '2017-12-31'], # Juleferien 2017/2018: Fra og med 22. desember til og med 1. januar
    ['2018-02-19', '2018-02-25'], # Vinterferie 2018: Fra og med 19. februar til og med 25. februar
    ['2018-03-29', '2018-04-02'], # MUST BE MARCH-APRIL, Påskeferie 2018: Fra og med 29. april til og med 2. april
    ['2018-05-11', '2018-05-11'], # Fri inneklemt dag 11. mai
    ['2018-06-22', '2018-08-17'], # sommerferien: 22. juni-17. august.
    ['2018-10-01', '2018-10-05'], # høstferie
    ]
def _is_school_holiday(row):
    date_str = row['DateTime'].strftime('%Y-%m-%d')
    for sh in _school_holidays:
        if sh[0] <= date_str <= sh[1]:
            return 1
    return 0


def create_calendar_df(yearly_ranges, summertime_season, time_delta_minutes):

    # concat for several years with a different range each
    df_date = [pd.DataFrame(
        {'DateTime': pd.date_range(start=yearly_ranges[year]['start'],
                                   end=yearly_ranges[year]['end'],
                                   freq='%dmin' % time_delta_minutes)})
        for year in yearly_ranges]

    df_date = pd.concat(df_date, ignore_index=True)
    df_date.DateTime.dt.tz_convert('UTC')
    df_date['hour'] = df_date['DateTime'].dt.hour
    df_date['weekday'] = df_date['DateTime'].dt.dayofweek
    df_date['month'] = df_date['DateTime'].dt.month
    df_date['public_holiday'] = df_date.apply(_is_public_holiday, axis=1)
    df_date['school_holiday'] = df_date.apply(_is_school_holiday, axis=1)

    # The 'hour' column should have the local time full hour.
    # CEST = UTC + 2 h
    # CET  = UTC + 1 h
    df_date['hour'] = df_date['hour'] + 1 # whole year
    for yr in summertime_season:
        mask = (df_date.DateTime > summertime_season[yr]['start'])& \
               (df_date.DateTime < summertime_season[yr]['end'])
        df_date.loc[mask, 'hour'] = df_date.loc[mask, 'hour'] + 1
    # Note that we may now have hours > 23. These have to be filtered out
    # together with the closing hours (0-6 local time) of the scheme.
    df_date = df_date[(df_date.hour >= 6)&(df_date.hour <= 23)]

    # Turn data into categorical.
    category_variable_list = ['hour', 'weekday', 'month', 'school_holiday',
                              'public_holiday']
    for var in category_variable_list:
        df_date[var] = df_date[var].astype('int32')
        df_date[var] = df_date[var].astype('category')

    return df_date
