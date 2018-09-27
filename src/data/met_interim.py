import numpy as np
import pandas as pd

class _WMO4677_translator(object):
    '''
    Translate from the standard codes to a system with just six categories.
    '''

    def __init__(self):
        self.__nr_of_categories = 6
        self.__cat_names = [
            'weather_fair/cloudy',  # 0
            'weather_fog/haze',  # , bad visibility: 1
            'weather_thunderstorm',  # thunder/lightning: 2
            'weather_rain',  # precipitation/hail: 3
            'weather_snow',  # 4
            'weather_other',  # 5
        ]
        self.__wc_dict = {
            0: 0,  # Cloud development not observed or not observable
            1: 0,  # Cloud generally dissolving or becoming less developed
            2: 0,  # State of sky on the whole unchanged
            3: 0,  # Clouds generally forming or developing
            4: 1,  # Visibility reduced by smoke, e.g. veldt or forest fires,
            # industrial smoke or volcanic ashes
            5: 1,  # Haze
            6: 1,
        # Widespread dust in suspension in the air, not raised by wind
            # at or near the station at the time of observation
            7: 1,
        # Dust or sand raised by wind at or near the station at the time
            # of  observation, but not well-developed dust whirl(s) or sand
            # whirl(s), and no duststorm or sandstorm seen; or, in the case
            # of ships, blowing spray at the station
            8: 1,  # Well-developed dust or sand whirl(s) seen at or near the
            # station during the preceding hour or at the time of
            # observation, but no dust storm or sandstorm
            9: 1,
        # Duststorm or sandstorm within sight at the time of observation,
            # or at the station during the preceding hour
            10: 1,  # Mist
            11: 1,
        # Patches of shallow fog or ice fog at the station, whether on
            # land or sea not deeper than about 2 metres on land or 10
            # metres at sea
            12: 1,
        # More or less continuous shallow fog or ice fog at the station,
            # whether on land or sea, not deeper than about 2m/land or
            # 10m/sea
            13: 2,  # Lightning visible, no thunder heard
            14: 3,  # Precipitation within sight, not reaching the ground or the
            # surface of the sea
            15: 3,
        # Precipitation within sight, reaching the ground or the surface
            # of the sea, but distant, i.e. > 5 km from the station
            16: 3,
        # Precipitation within sight, reaching the ground or the surface
            # of the sea, near to, but not at the station
            17: 2,
        # Thunderstorm, but no precipitation at the time of observation
            18: 3,
        # Squalls at or within sight of the station during the preceding
            # hour or at the time of observation
            19: 5,  # Funnel clouds at or within sight of the station during the
            # preceding hour or at the time of observation
            20: 3,  # Drizzle (not freezing) or snow grains, not falling as
            # showers, during the preceding hour but not at the time of
            # observation
            21: 3,  # Rain (not freezing), not falling as showers, during the
            # preceding hour but not at the time of observation
            22: 4,
        # Snow, not falling as showers, during the preceding hour but
            # not at the time of observation
            23: 3,  # Rain and snow or ice pellets, not falling as showers;
            # during the preceding hour but not at the time of observation
            24: 4,
        # Freezing drizzle or freezing rain; during the preceding hour
            # but not at the time of observation
            25: 3,  # Shower(s) of rain during the preceding hour but not at the
            # time of observation
            26: 4,
        # Shower(s) of snow, or of rain and snow during the preceding
            # hour but not at the time of observation
            27: 3,
        # Shower(s) of hail, or of rain and hail during the preceding
            # hour but not at the time of observation
            28: 1,  # Fog or ice fog during the preceding hour but not at the
            # time of observation
            29: 2,  # Thunderstorm (with or without precipitation) during the
            # preceding hour but not at the time of observation
            30: 1,  # Slight or moderate duststorm or sandstorm:
            # has decreased during the preceding hour
            31: 1,  # Slight or moderate duststorm or sandstorm:
            # no appreciable change during the preceding hour
            32: 1,  # Slight or moderate duststorm or sandstorm:
            # has begun or has increased during the preceding hour
            33: 1,  # Severe duststorm or sandstorm:
            # has decreased during the preceding hour
            34: 1,  # Severe duststorm or sandstorm:
            # no appreciable change during the preceding hour
            35: 1,  # Severe duststorm or sandstorm:
            # has begun or has increased during the preceding hour
            36: 4,  # Slight/moderate drifting snow:
            # generally low (below eye level)
            37: 4,  # Heavy drifting snow: generally low (below eye level)
            38: 4,
        # Slight/moderate blowing snow: generally high (above eye level)
            39: 4,  # Heavy blowing snow: generally high (above eye level)
            40: 1,  # Fog or ice fog at a a distance at the time of observation,
            # but not at station during the preceding hour, the fog or
            # ice fog extending to a level above that of  the observer
            41: 1,  # Fog or ice fog in patches
            42: 1,  # Fog/ice fog, sky visible, has become thinner during the
            # preceding hour
            43: 1,  # Fog/ice fog, sky invisible, has become thinner during the
            # preceding hour
            44: 1,
        # Fog or ice fog, sky visible, no appreciable change during the
            # past hour
            45: 1,
        # Fog or ice fog, sky invisible, no appreciable change during
            # the preceding hour
            46: 1,
        # Fog or ice fog, sky visible, has begun or has become thicker
            # during preceding hour
            47: 1,  # Fog or ice fog, sky invisible, has begun or has become
            # thicker during the preceding hour
            48: 1,  # Fog, depositing rime, sky visible
            49: 1,  # Fog, depositing rime, sky invisible
            50: 3,  # Drizzle, not freezing, intermittent, slight at time of ob.
            51: 3,  # Drizzle, not freezing, continuous, slight at time of ob.
            52: 3,
        # Drizzle, not freezing, intermittent, moderate at time of ob.
            53: 3,  # Drizzle, not freezing, continuous, moderate at time of ob.
            54: 3,  # Drizzle, not freezing, intermittent, heavy at time of ob.
            55: 3,  # Drizzle, not freezing, continuous, heavy at time of ob.
            56: 3,  # Drizzle, freezing, slight
            57: 3,  # Drizzle, freezing, moderate or heavy (dense)
            58: 3,  # Rain and drizzle, slight
            59: 3,  # Rain and drizzle, moderate or heavy
            60: 3,  # Rain, not freezing, intermittent, slight at time of ob.
            61: 3,  # Rain, not freezing, continuous, slight at time of ob.
            62: 3,  # Rain, not freezing, intermittent, moderate at time of ob.
            63: 3,  # Rain, not freezing, continuous, moderate at time of ob.
            64: 3,  # Rain, not freezing, intermittent, heavy at time of ob.
            65: 3,  # Rain, not freezing, continuous, heavy at time of ob.
            66: 3,  # Rain, freezing, slight
            67: 3,  # Rain, freezing, moderate or heavy
            68: 3,  # Rain or drizzle and snow, slight
            69: 3,  # Rain or drizzle and snow, moderate or heavy
            70: 4,  # Intermittent fall of snowflakes, slight at time of ob.
            71: 4,  # Continuous fall of snowflakes, slight at time of ob.
            72: 4,  # Intermittent fall of snowflakes, moderate at time of ob.
            73: 4,  # Continuous fall of snowflakes, moderate at time of ob.
            74: 4,  # Intermittent fall of snowflakes, heavy at time of ob.
            75: 4,  # Continuous fall of snowflakes, heavy at time of ob.
            76: 4,  # Diamond dust (with or without fog)
            77: 4,  # Snow grains (with or without fog)
            78: 4,  # Isolated star-like snow crystals (with or without fog)
            79: 4,  # Ice pellets
            80: 3,  # Rain shower(s), slight
            81: 3,  # Rain shower(s), moderate or heavy
            82: 3,  # Rain shower(s), violent
            83: 3,  # Shower(s) of rain and snow, slight
            84: 3,  # Shower(s) of rain and snow, moderate or heavy
            85: 4,  # Snow shower(s), slight
            86: 4,  # Snow shower(s), moderate or heavy
            87: 4,  # Shower(s) of snow pellets or small hail, with or without
            # rain or rain and snow mixed: , # slight
            88: 4,  # Shower(s) of snow pellets or small hail, with or without
            # rain or rain and snow mixed: , # moderate or heavy
            89: 4,  # Shower(s) of hail, with or without rain or rain and snow
            # mixed, not associated with thunder: , # slight
            90: 4,  # Shower(s) of hail, with or without rain or rain and snow
            # mixed, not associated with thunder: , # moderate or heavy
            91: 2,
        # Slight rain at time of observation: , # Thunderstorm during
            # the preceding hour but not at time of observation
            92: 2,  # Moderate or heavy rain at time of observation:
            # Thunderstorm during the preceding hour but not at time of
            # observation
            93: 2,  # Slight snow, or rain and snow mixed or hail at time of
            # observation: Thunderstorm during the preceding hour but not
            # at time of observation
            94: 2,  # Moderate or heavy snow, or rain and snow mixed or hail at
            # time of observation: Thunderstorm during the preceding hour
            # but not at time of observation
            95: 2,  # Thunderstorm, slight or moderate, without hail, but with
            # rain and/or snow at time of observation
            96: 2,  # Thunderstorm, slight or moderate, with hail at time of ob.
            97: 2,  # Thunderstorm, heavy, without hail, but with rain and/or
            # snow at time of observation
            98: 2,  # Thunderstorm combined with dust/sandstorm at time of
            # observation
            99: 2,  # Thunderstorm, heavy with hail at time of observation
        }

    def met2cat(self, met_code):
        return self.__wc_dict[met_code]

    def cat_name(self, cat):
        return self.__cat_names[cat]

    def nr_of_categories(self):
        return self.__nr_of_categories


def _met_transform_weather(df, delete_original=True):
    '''Observations of the current weather phenomena are given in up to three
    columns at observation times, i.e. every 3rd hour, except at night.
    Transform the numerical codes to a small number of categories, stored
    as 1-hot-encoding. In addition, fill downwards to the following two hours
    after each observation. If all of the categories are zero, then no
    observation was available at the time -- typically this affects night time
    from 21 to 05.'''
    translator = _WMO4677_translator()

    # create new feature columns
    for ic in range(translator.nr_of_categories()):
        df[translator.cat_name(ic)] = np.nan

    for index, row in df.iterrows():
        for col in ['weather1', 'weather2', 'weather3']:
            if not np.isnan(row[col]):
                met_code = int(row[col])
                cat = translator.met2cat(met_code)
                df.loc[index, translator.cat_name(cat)] = 1

    for ic in range(translator.nr_of_categories()):
        # Fill the remaining nans with 0.
        cat_name = translator.cat_name(ic)
        df[cat_name].fillna(value=0, inplace=True)
        df[cat_name] = df[cat_name].astype('int32')

    if delete_original:
        for col in ['weather1', 'weather2', 'weather3']:
            df.drop(columns=col, inplace=True)

    return df


def fill_met_data(df_met, df_date, time_delta_minutes):
    '''In the met data, some hours are missing completely. So before we can
    start to fill values downwards we have to make sure that all rows are
    present. To do that, we merge with the days dataframe, which has one
    row per delta_'''
    df_joined = pd.merge(df_date, df_met, left_on='DateTime', right_on='index',
                         how='left')
    df_joined.drop(columns=['index'], inplace=True)
    # fill observed variables
    interpolate_only  = {'solar_elevation_angle'}
    interpolate_extra = {'air_temperature', 'max(wind_speed PT1H)',
                         'max_wind_speed(wind_from_direction PT1H)',
                         'relative_humidity', 'sum(precipitation_amount PT1H)'}
    fill_3h_backwards = {'weather_type'}
    fill_6h_backwards = {'over_time(weather_type_primary_significance PT6H)',
                         'over_time(weather_type_secondary_significance PT6H)'}
    fill_1h_backwards = set(df_joined.columns) - fill_3h_backwards \
                        - fill_6h_backwards - interpolate_only
    limit_1h = int(60 / time_delta_minutes - 1)
    limit_3h = int(180 / time_delta_minutes - 1)
    limit_6h = int(360 / time_delta_minutes - 1)
    if limit_3h > 0:
        for var in fill_3h_backwards:
            df_joined[var].fillna(method='backfill', limit=limit_3h,
                                  inplace=True)
    if limit_6h > 0:
        for var in fill_6h_backwards:
            df_joined[var].fillna(method='backfill', limit=limit_6h,
                                  inplace=True)
    if limit_1h > 0:
        for var in fill_1h_backwards:
            df_joined[var].fillna(method='backfill', limit=limit_1h,
                                  inplace=True)

    # for some variable we allow us to stretch the filling a bit more with
    # interpolation; note that these were filled up to a range already above,
    # i.e. they are different from the solar elevation which is only
    # interpolated
    for var in interpolate_only | interpolate_extra:
        df_joined[var].interpolate(method='linear', inplace=True)

    # The sunshine-variable is the only one that has nan-values left now.
    # Let's set these to zero.
    df_joined['sum(duration_of_sunshine PT1H)'].fillna(value=0, inplace=True)

    return df_joined


def transform_variables(df_met):
    # 1) Assign shorter, easy-to-understand column names.
    df_met.rename(columns={
        'air_temperature': 'temperature',
        'max(wind_speed PT1H)': 'wind_speed',
        'max_wind_speed(wind_from_direction PT1H)': 'wind_direction',
        'relative_humidity': 'humidity',
        'sum(duration_of_sunshine PT1H)': 'sunshine',
        'weather_type': 'weather1',
        'over_time(weather_type_primary_significance PT6H)': 'weather2',
        'over_time(weather_type_secondary_significance PT6H)': 'weather3',
        'sum(precipitation_amount PT1H)': 'precipitation',
    }, inplace=True)

    # 2) Transform wind direction in degrees to categories
    #    categories returned: 0 = symmetric around North (0 degrees), otherwise
    #    rising towards bigger angles; range = [0, nr_of_categories-1].
    nr_of_categories = 8
    degrees_per_cat = 360. / nr_of_categories
    df_met['wind_direction_cat'] = df_met.wind_direction.apply(
            lambda phi: int((phi + degrees_per_cat / 2.) / degrees_per_cat) %
                        nr_of_categories)
    df_met['wind_direction_cat'].astype('category')
    if True: # delete_original:
        df_met.drop(columns='wind_direction', inplace=True)

    # 3) Transform the weather observations to something simpler.
    df_met = _met_transform_weather(df_met)

    return df_met


def sun_below_horizon(df_met):
    for index, row in df_met.iterrows():
        if row['solar_elevation_angle'] < 0 and row['sunshine'] > 0:
            print(index, row)