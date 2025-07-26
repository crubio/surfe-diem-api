from dataclasses import dataclass
from typing import Any, Dict

@dataclass
class SpotLocation:
    id: Any
    name: str
    timezone: str
    latitude: float
    longitude: float
    subregion_name: str

    @classmethod
    def from_obj(cls, spot_location):
        return cls(
            id=spot_location.id,
            name=spot_location.name,
            timezone=spot_location.timezone,
            latitude=spot_location.latitude,
            longitude=spot_location.longitude,
            subregion_name=spot_location.subregion_name
        )

    def get_geojson(self) -> Dict:
        return {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [self.longitude, self.latitude],  # GeoJSON: [lon, lat]
            },
            "properties": {
                "id": self.id,
                "name": self.name,
                "timezone": self.timezone,
                "subregion_name": self.subregion_name,
            }
        }