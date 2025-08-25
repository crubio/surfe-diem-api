"""
Tides Service

This service handles all tide-related business logic, database operations,
and orchestrates calls to the NOAA Tides Client.
"""

from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from geopy import distance
from ..models import TideStation
from ..clients.noaa_tides_client import NOAATidesClient
from ..schemas import (
    CurrentTidesRequest,
    HistoricalTidesRequest,
    TideStationDistance,
    TideStation as TideStationSchema,
    TideStationsListResponse
)


class TidesService:
    """Service for handling tide-related business logic and database operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.noaa_client = NOAATidesClient()
    
    async def get_current_tides(self, request: CurrentTidesRequest) -> Dict[str, Any]:
        """
        Get current tide data for a specific station
        
        Args:
            request: CurrentTidesRequest with station and parameters
            
        Returns:
            NOAA API response as dict
        """
        async with self.noaa_client as client:
            return await client.get_current_tides(request)
    
    async def get_tides_summary(self, request: HistoricalTidesRequest) -> Dict[str, Any]:
        """
        Get tide summary (hilo range) for last 2 high and low tides
        
        Args:
            request: HistoricalTidesRequest with station and parameters
            
        Returns:
            NOAA API response with hilo data
        """
        # Override some defaults for hilo summary
        hilo_request = HistoricalTidesRequest(
            station=request.station,
            product="predictions",
            datum=request.datum,
            time_zone=request.time_zone,
            interval="hilo",  # Force hilo interval for summary
            units=request.units,
            application=request.application,
            format=request.format
        )
        
        async with self.noaa_client as client:
            return await client.get_historical_tides(hilo_request)
    
    def find_closest_tide_station(self, lat: float, lng: float, max_distance: float = 100) -> TideStationDistance:
        """
        Find the closest tide station to given coordinates
        
        Args:
            lat: Latitude
            lng: Longitude  
            max_distance: Maximum search radius in miles
            
        Returns:
            TideStationDistance with closest station info
            
        Raises:
            ValueError: If no stations found within range
        """
        stations = self.db.query(TideStation.station_id, TideStation.latitude, TideStation.longitude).all()
        
        if not stations:
            raise ValueError("No tide stations found in database")
        
        best_stations = []
        for station in stations:
            station_distance = distance.distance((lat, lng), (station.latitude, station.longitude)).miles
            if station_distance < max_distance:
                best_stations.append({
                    "station_id": station.station_id,
                    "distance": station_distance,
                    "latitude": station.latitude,
                    "longitude": station.longitude
                })
        
        if not best_stations:
            raise ValueError(f"No tide stations found within {max_distance} miles of coordinates ({lat}, {lng})")
        
        # Return closest station
        closest = min(best_stations, key=lambda x: x['distance'])
        return TideStationDistance(**closest)
    
    def get_tide_stations(self, limit: int = 100, offset: int = 0) -> TideStationsListResponse:
        """
        Get paginated list of tide stations
        
        Args:
            limit: Number of stations to return
            offset: Number of stations to skip
            
        Returns:
            TideStationsListResponse with stations and pagination info
        """
        stations = self.db.query(TideStation).offset(offset).limit(limit).all()
        
        if not stations:
            raise ValueError("No tide stations found in database")
        
        station_schemas = [
            TideStationSchema(
                id=station.id,
                station_id=station.station_id,
                station_name=station.station_name,
                latitude=station.latitude,
                longitude=station.longitude
            )
            for station in stations
        ]
        
        return TideStationsListResponse(
            stations=station_schemas,
            total=len(station_schemas),
            limit=limit,
            offset=offset
        )
    
    def get_tide_station_by_id(self, station_id: str) -> TideStationSchema:
        """
        Get a specific tide station by station_id
        
        Args:
            station_id: NOAA station ID
            
        Returns:
            TideStationSchema with station data
            
        Raises:
            ValueError: If station not found
        """
        station = self.db.query(TideStation).filter(
            TideStation.station_id == station_id
        ).first()
        
        if not station:
            raise ValueError(f"Tide station {station_id} not found")
        
        return TideStationSchema(
            id=station.id,
            station_id=station.station_id,
            station_name=station.station_name,
            latitude=station.latitude,
            longitude=station.longitude
        )
    
    def delete_tide_station(self, station_id: str) -> None:
        """
        Delete a tide station by station_id
        
        Args:
            station_id: NOAA station ID
            
        Raises:
            ValueError: If station not found
        """
        station = self.db.query(TideStation).filter(
            TideStation.station_id == station_id
        ).first()
        
        if not station:
            raise ValueError(f"Tide station {station_id} not found")
        
        self.db.delete(station)
        self.db.commit()
