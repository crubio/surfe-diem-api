import httpx
import json

class BuoyLatestObservation():
    '''Get & parse latest observation from various NOAA feeds'''
    def __init__(self, location_id):

        self.location_id = location_id
        
    # Probably don't use this one
    @property
    def latest_reading_rss_url(self):
        return f"https://www.ndbc.noaa.gov/data/latest_obs/{self.location_id}.rss"

    @property
    def latest_observation_url(self):
        return f"https://www.ndbc.noaa.gov/data/latest_obs/{self.location_id}.txt"
    
    def url(self):
        return self.latest_observation_url
    
    def parse_latest_reading_data(self, raw_data):
        print('parse_latest_reading_data')
        raw_data = raw_data.split('\n')
        swell_period_read = False
        swell_direction_read = False
        # TODO: create a class for buoy data
        wave_summary = {}
        swell_component = {}
        wind_wave_component = {}

        for i in range(5, len(raw_data)):
            if raw_data[i] == '':
                continue
            parts = raw_data[i].split(':')
            variable = parts[0].lower()

            if variable == 'seas':
                wave_summary['wave_height'] = parts[1].strip()
            elif variable == 'peak period':
                wave_summary['peak_period'] = parts[1].strip()
            elif variable == 'water temp':
                wave_summary['water_temp'] = parts[1].strip()
            elif variable == 'pres':
                wave_summary['atmospheric_pressure'] = parts[1].strip()
            elif variable == 'air temp':
                wave_summary['air_temp'] = parts[1].strip()
            elif variable == 'dew point':
                wave_summary['dew_point'] = parts[1].strip()
            elif variable == 'swell':
                swell_component['swell_height'] = parts[1].strip()
            elif variable == 'period':
                if not swell_period_read:
                    swell_component['period'] = parts[1].strip()
                    swell_period_read = True
                else:
                    wind_wave_component['period'] = parts[1].strip()
            elif variable == 'direction':
                if not swell_direction_read:
                    swell_component['direction'] = parts[1].strip()
                    swell_direction_read = True
                else:
                    wind_wave_component['direction'] = parts[1].strip()
            elif variable == 'wind wave':
                wind_wave_component['wind_wave_height'] = parts[1].strip()

        return [wave_summary, swell_component, wind_wave_component]
