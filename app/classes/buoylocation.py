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
        
        return [float(parts[0]), float(parts[2])] # [lon, lat]
    
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