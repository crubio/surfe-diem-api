"""
NOAA Tides Client

This client encapsulates all NOAA Tides and Currents API interactions.
It handles HTTP requests, response parsing, and error handling for tide-related endpoints.
"""

import httpx
from typing import Dict, Any, Optional
from ..schemas import (
    CurrentTidesRequest,
    HistoricalTidesRequest,
    TideStationSearchRequest,
    TideStationsListRequest
)

APPLICATION: str = "surfe-diem.com"
TIDES_URL: str = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
FORMAT: str = "JSON"
CACHE_TTL_SECONDS: int = 360 # cache all results for 1 hr


class NOAATidesClient:
    """Client for interacting with NOAA Tides and Currents API"""
    
    def __init__(self, base_url: str = TIDES_URL):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def get_current_tides(self, request: CurrentTidesRequest) -> Dict[str, Any]:
        """
        Get current tide data for a specific station
        
        Args:
            request: CurrentTidesRequest with station and parameters
            
        Returns:
            NOAA API response as dict
        """
        params = self._build_current_tides_params(request)
        response = await self.client.get(self.base_url, params=params)
        return self._handle_response(response)
    
    async def get_historical_tides(self, request: HistoricalTidesRequest) -> Dict[str, Any]:
        """
        Get historical tide data for a specific station and date range
        
        Args:
            request: HistoricalTidesRequest with station and date parameters
            
        Returns:
            NOAA API response as dict
        """
        params = self._build_historical_tides_params(request)
        response = await self.client.get(self.base_url, params=params)
        return self._handle_response(response)
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
    
    def _build_current_tides_params(self, request: CurrentTidesRequest) -> Dict[str, str]:
        """Build query parameters for current tides request"""
        return {
            "station": request.station,
            "interval": request.interval,
            "product": request.product,
            "datum": request.datum,
            "time_zone": request.time_zone,
            "units": request.units,
            "application": request.application or APPLICATION,
            "format": request.format or FORMAT,
            "date": request.date
        }
    
    def _build_historical_tides_params(self, request: HistoricalTidesRequest) -> Dict[str, str]:
        """Build query parameters for historical tides request"""
        params = {
            "station": request.station,
            "product": request.product,
            "datum": request.datum,
            "date": request.date,
            "time_zone": request.time_zone,
            "interval": request.interval,
            "units": request.units,
            "application": request.application or APPLICATION,
            "format": request.format or FORMAT
        }
        
        if request.begin_date:
            params["begin_date"] = request.begin_date
        if request.end_date:
            params["end_date"] = request.end_date
            
        return params
    
    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Handle NOAA API response and errors"""
        try:
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as exc:
            # Network/connection errors
            raise Exception(f"Failed to connect to NOAA API: {exc.request.url!r}")
        except httpx.HTTPStatusError as exc:
            # HTTP error responses
            raise Exception(f"NOAA API error: {exc.response.status_code} - {exc.response.reason_phrase}")
        except Exception as exc:
            # Other errors (JSON parsing, etc.)
            raise Exception(f"Unexpected error processing NOAA response: {str(exc)}")
