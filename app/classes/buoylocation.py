import pandas as pd
from dataclasses import dataclass
from typing import Any
import re

class BuoyData:
    def __init__(self) -> None:
        self.location_id: str | None = None
        self.data: pd.DataFrame | None = None
        self.url: str | None = None

class BuoyDataBuilder:
    def __init__(self) -> None:
        self.base_url: str = 'https://www.ndbc.noaa.gov/data/realtime2/'

    def build(self, location_id: str, data: list[str]) -> BuoyData:
        url = self.base_url + location_id + '.txt'
        df = self._mk_dataframe(data)
        buoy_data = BuoyData()
        buoy_data.location_id = location_id
        buoy_data.data = df
        buoy_data.url = url
        return buoy_data

    def _mk_dataframe(self, data: list[str]) -> pd.DataFrame:
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

        

@dataclass
class BuoyLocation:
    """Represents a NOAA buoy location with parsing and GeoJSON export capabilities."""
    location: str
    location_id: str
    name: str
    url: str
    description: str

    def parse_location(self) -> list[float]:
        """
        Parse the location string to [longitude, latitude].
        Supports formats like '34.5 N 120.5 W', '34.5N 120.5W', etc.
        Returns:
            [longitude, latitude]
        Raises:
            ValueError: if the format is invalid.
        """
        pattern = r"([+-]?\d+(?:\.\d+)?)\s*([NS])[, ]+([+-]?\d+(?:\.\d+)?)\s*([EW])"
        match = re.search(pattern, self.location.strip().replace(',', ' '))
        if not match:
            raise ValueError(f"Invalid location format: {self.location}")

        lat, lat_dir, lon, lon_dir = match.groups()
        lat = float(lat) * (-1 if lat_dir.upper() == 'S' else 1)
        lon = float(lon) * (-1 if lon_dir.upper() == 'W' else 1)

        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValueError("Latitude or longitude out of range")

        return [lon, lat]  # GeoJSON: [longitude, latitude]

    def get_geojson(self) -> dict:
        """
        Return a GeoJSON feature for this buoy location.
        Returns:
            dict: GeoJSON feature representation of the buoy location.
        """
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

    @classmethod
    def from_obj(cls, buoy_location: Any) -> "BuoyLocation":
        """
        Instantiate a BuoyLocation from an object with matching attributes.
        Args:
            buoy_location (Any): An object with location, location_id, name, url, and description attributes.
        Returns:
            BuoyLocation: An instance of the dataclass.
        """
        return cls(
            location=buoy_location.location,
            location_id=buoy_location.location_id,
            name=buoy_location.name,
            url=buoy_location.url,
            description=buoy_location.description
        )