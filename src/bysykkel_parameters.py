# -*- coding: utf-8 -*-
"""
Created on Sat Sep 22 10:37:57 2018

@author: lpesch
"""
from datetime import datetime as dt
from datetime import timezone as tz

max_trip_duration_seconds = 4 * 3600
time_delta_minutes = 60

# All time data is in UTC (both met and trip data).
service_season = {
    2016: {'start': dt(2016,  4,  1,  7,  0, tzinfo=tz.utc),
           'end':   dt(2016, 12,  6,  0,  0, tzinfo=tz.utc)},
    2017: {'start': dt(2017,  4,  1,  9,  0, tzinfo=tz.utc),
           'end':   dt(2017, 12, 10,  5,  0, tzinfo=tz.utc)},
    # Note: 201803 data seems to be testing only, therefore neglected.
    2018: {'start': dt(2018,  4,  1, 15,  0, tzinfo=tz.utc),
           'end':   dt(2018,  8, 31, 23, 59, tzinfo=tz.utc)}, # current
    }

# CEST = UTC + 2 h
# CET  = UTC + 1 h
summertime_season = {
    2016: {'start': dt(2016,  3, 27, 2, 0, tzinfo=tz.utc),
           'end':   dt(2016, 10, 30, 3, 0, tzinfo=tz.utc)},
    2017: {'start': dt(2017,  3, 26, 2, 0, tzinfo=tz.utc),
           'end':   dt(2017, 10, 29, 3, 0, tzinfo=tz.utc)},
    2018: {'start': dt(2018,  3, 25, 2, 0, tzinfo=tz.utc),
           'end':   dt(2018, 10, 28, 3, 0, tzinfo=tz.utc)},
    }