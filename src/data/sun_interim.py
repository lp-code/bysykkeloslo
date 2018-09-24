import astropy.coordinates as coord
from astropy.time import Time
import astropy.units as u
import pandas as pd

_loc_blindern = coord.EarthLocation(lon=10.72 * u.deg,
                                    lat=59.92 * u.deg)

def calculate_elevation(tt, loc=_loc_blindern):
    sun_time = Time(tt)
    if ( (tt.hour == 0) and (tt.minute == 0) ):
        print(f'Calculate solar elevation angle for: {sun_time}')
    zen_ang = coord.get_sun(sun_time).transform_to(
        coord.AltAz(obstime=sun_time, location=loc)).alt.degree
    return zen_ang

'''
def elevation_to_category(solar_elevation,degrees_per_cat,nr_of_categories):
    upper = 0.
    for icategory in range(nr_of_categories):
        if (solar_elevation < upper):
            return icategory
        upper += degrees_per_cat
    return nr_of_categories
'''

def create_solar_elevation_column(df_met):
    df_met['solar_elevation_angle'] = df_met['index'].apply(calculate_elevation)
    return df_met


