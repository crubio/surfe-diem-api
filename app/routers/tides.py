import httpx
from typing import Union
from .. import models
from fastapi import Depends, HTTPException, status, APIRouter
from geopy import distance
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.tides_service import TidesService
from ..schemas import CurrentTidesRequest, HistoricalTidesRequest
from .. import schemas, oauth2

router = APIRouter(
    prefix="/api/v1",
    tags=["Tides"]
)

@router.get("/tides/find_closest")
def get_closest_tide_station(
    lat: float,
    lng: float,
    dist: float = 50,
    db: Session = Depends(get_db)
):
    """Find the closest tide station within the specified distance radius."""
    try:
        tides_service = TidesService(db)
        return tides_service.find_closest_tide_station(lat, lng, dist)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=str(e)
        )

@router.get("/tides/current")
async def get_current_tides(
    station: str,
    db: Session = Depends(get_db)
):
    """Get current water level data for a specific tide station."""
    try:
        tides_service = TidesService(db)
        request = CurrentTidesRequest(station=station)
        return await tides_service.get_current_tides(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=str(e)
        )
    
@router.get("/tides")
async def get_tides_summary(
    station: str,
    db: Session = Depends(get_db)
):
    """Get tide summary (last 2 high/low tides) for a specific station."""
    try:
        tides_service = TidesService(db)
        request = HistoricalTidesRequest(station=station)
        return await tides_service.get_tides_summary(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=str(e)
        )
    
@router.get("/tides/stations")
def get_all_tide_stations(
    limit: int = 100, 
    offset: int = 0, 
    db: Session = Depends(get_db)
):
    """Get paginated list of all tide stations for admin auditing."""
    try:
        tides_service = TidesService(db)
        return tides_service.get_tide_stations(limit=limit, offset=offset)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=str(e)
        )

@router.get("/tides/stations/{station_id}")
def get_tide_station_by_id(station_id: str, db: Session = Depends(get_db)):
    """Get metadata for a specific tide station by ID."""
    try:
        tides_service = TidesService(db)
        return tides_service.get_tide_station_by_id(station_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=str(e)
        )

@router.delete("/tides/stations/{station_id}")
def delete_tide_station(
    station_id: str, 
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(oauth2.get_current_user)
):
    """Delete a tide station (admin only)."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        tides_service = TidesService(db)
        tides_service.delete_tide_station(station_id)
        return {"message": f"Tide station {station_id} deleted successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )