#!/usr/bin/python

"""
To run this code you must have a file frost_account.py accessible in your
python path directories, which contains a variable client_id with the id
you got from https://frost.met.no/

References:
    https://frost.met.no/elementtable
    http://eklima.met.no/Help/Stations/toDay/all/en_stations.html
"""

import sys
import dateutil.parser as dp
import requests # See http://docs.python-requests.org/
import numpy as np
import pandas as pd
#from pprint import pprint
import frost_account

if __name__ == "__main__":

    station = 'SN18700'                                     # Oslo Blindern
    elements = ['air_temperature',                          # TA
                'max(wind_speed PT1H)',                     # FX_1 max mean 1h
                'max_wind_speed(wind_from_direction PT1H)', # DX_1 direction
                # 'wind_speed',                               # FF, 10 min avg
                # 'wind_from_direction',                      # DD
                'relative_humidity',                        # UU
                'weather_type',                             # WW, only every 3 h from 09 to 18
                #'weather_type_automatic',                   # WAWA, 90% are 0
                # 'over_time(weather_type_primary_significance PT3H)', # W1, no data
                # 'over_time(weather_type_secondary_significance PT3H)', # W2, no data
                'over_time(weather_type_primary_significance PT6H)', # W1
                'over_time(weather_type_secondary_significance PT6H)', # W2
                # 'over_time(weather_type_additional1 PT6H)', # WD1, almost no data
                # 'over_time(weather_type_additional2 PT6H)', # WD2, almost no data
                # 'air_pressure_at_sea_level',                # PR
                # 'cloud_area_fraction',                      # NN, only daytime
                ]

    _station = 'SN18701'                                     # Oslo Blindern
    _elements = ['sum(precipitation_amount PT1H)',           # RR_1 last hour
                'sum(duration_of_sunshine PT1H)',           # OT_1	 sunshine last hour
                ]
    

    # The time interval on frost is given as UTC, trip data is in local time.
    # CEST = UTC + 2 h
    # But since we do not consider the time from 0 to 04 on the first day,
    # we do not need extra data because of UTC-CE(S)T conversion.
    time_interval = '2017-04-01T00:00/2017-04-30T23:59'
    get_met_data = True
    verbose = False

    r_src = requests.get(
        'https://frost.met.no/sources/v0.jsonld',
        {'ids': station},
        auth=(frost_account.client_id, ''))
    if r_src.status_code == 200:
        data_src = r_src.json()['data'][0]
        print('Retrieving data for: {} ({})'.format(data_src['name'], data_src['id']))
 
    
    if get_met_data:
        r = requests.get(
            'https://frost.met.no/observations/v0.jsonld',
            {'sources': station,
             'elements': ','.join(elements),
             'referencetime': time_interval},
            auth=(frost_account.client_id, '')
        )
        json = r.json()
        #with open('tmp.dat', 'w') as f:
        #    pprint(json, f)
           
        # extract the time series from the response
        if r.status_code == 200:
            datetime_list = []
            met_values = np.empty((json['itemsPerPage'], len(elements)))
            met_values.fill(np.nan)
            time_index = 0
            
            for item in json['data']:
                datetime_obj = dp.parse(item['referenceTime'])
                datetime_list.append(datetime_obj)
                for variable in item['observations']:
                    met_values[time_index, elements.index(variable['elementId'])] = variable['value']
                time_index += 1
                
                if verbose:
                    datetime_str = datetime_obj.strftime('%Y-%m-%d %H:%M:%S%z')
                    sys.stdout.write('{}\n'.format(datetime_str))

            df = pd.DataFrame(index=pd.DatetimeIndex(data=datetime_list),
                              data=met_values,
                              columns=elements)
            print(df.describe())
            df.to_pickle('blindern_met.pck')
        else:
            sys.stdout.write('error:\n')
            sys.stdout.write('\tstatus code: {}\n'.format(r.status_code))
            if 'error' in r.json():
                assert(r.json()['error']['code'] == r.status_code)
                sys.stdout.write('\tmessage: {}\n'.format(r.json()['error']['message']))
                sys.stdout.write('\treason: {}\n'.format(r.json()['error']['reason']))
            else:
                sys.stdout.write('\tother error\n')
    