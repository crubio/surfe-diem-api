class SpotLocation():
    def __init__(self, spot_location):
        self.id = spot_location.id
        self.name = spot_location.name
        self.timezone = spot_location.timezone
        self.latitude = spot_location.latitude
        self.longitude = spot_location.longitude
        self.subregion_name = spot_location.subregion_name
    
    def get_geojson(self):
        feature_object = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [float(self.longitude), float(self.latitude)]
            },
            "properties": {
                "id": self.id,
                "name": self.name,
                "timezone": self.timezone,
                "subregion_name": self.subregion_name,
            }
        }
        return feature_object