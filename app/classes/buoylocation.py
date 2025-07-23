import pandas as pd

class BuoyData():
    def __init__ (self):
        self.location_id = None
        self.data = None

    def set_data(self, data):
        self.data = data

    def get_data(self):
        if self.data is None:
            self.data = pd.DataFrame()
        return self.data
    
class BuoyDataBuilder():
    def __init__(self):
        self.base_url = 'https://www.ndbc.noaa.gov/data/realtime2/'
        self.realtime_buoy = BuoyData()

    def build(self, location_id, data):
        self.realtime_buoy.url = self.base_url + location_id + '.txt'
        self.realtime_buoy.location_id = location_id
        self.realtime_buoy.set_data(self._mk_dataframe(data))

        return self.realtime_buoy

    def _mk_dataframe(self, data):
        try:
            df = pd.DataFrame([x.split() for x in data], columns=[
                "YY", "MM", "DD", "hh", "mm", "wind_dir", "wind_speed", "gst",
                "wave_height", "dominant_period", "avg_period", "pressure",
                "water_temp", "air_temp", "dew_point", "visibility", "pdty", "tide", "end_of_line"
            ])
        except Exception as e:
            print(f"Error creating DataFrame: {e}")
            df = pd.DataFrame()

        return df

        

class BuoyLocation():
    def __init__(self, buoy_location):
        self.location = buoy_location.location
        self.location_id = buoy_location.location_id
        self.name = buoy_location.name
        self.url = buoy_location.url
        self.description = buoy_location.description

    def parse_location(self):
        location_string = self.location
        parts = location_string.strip().split('(')[0].split(' ')
        
        if parts[1] == 'S':
            parts[0] = '-' + parts[0]
        if parts[3] == 'W':
            parts[2] = '-' + parts[2]
        
        return [float(parts[0]), float(parts[2])]
    
    def get_geojson(self):
        latlng = self.parse_location()
        feature_object = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": latlng
            },
            "properties": {
                "id": self.location_id,
                "name": self.name,
                "description": self.description,
                "url": self.url,
                "location": self.location,
            }
        }
        return feature_object