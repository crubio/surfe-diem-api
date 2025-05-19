from typing import List, Union, Optional
import httpx

from fastapi import Depends, HTTPException, Response, status, APIRouter
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from geopy import distance

from ..database import get_db
from .. import models, oauth2
from ..schemas import (BuoyLocationNOAASummary, BuoyLocationPost, BuoyLocationResponse, BuoyLocationPut, BuoyLocationLatestObservation, SpotLocationResponse)
from ..classes import buoylatestobservation as buoy, buoylocation as buoy_location, spotlocation as spot_location

router = APIRouter(
    prefix="/api/v1",
    tags=["Locations"]
)

@router.get("/search")
def search_all(db: Session = Depends(get_db), limit: int = 100, q: Optional[str] = ""):
    '''Search all locations & spots'''
    buoy_statement = select(
        models.BuoyLocation
    ).where(
        models.BuoyLocation.name.like(f"%{q}%")
    ).limit(limit)

    spot_statement = select(
        models.SpotLocation
    ).where(
        models.SpotLocation.name.like(f"%{q}%")
    ).limit(limit)

    buoy_locations = db.execute(buoy_statement).all()
    spot_locations = db.execute(spot_statement).all()

    if not buoy_locations and not spot_locations:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="no results found")
    
    locations_list = []
    for row in buoy_locations:
        locations_list.append(row[0])
    for row in spot_locations:
        locations_list.append(row[0])

    return locations_list

@router.get("/spots", response_model=List[SpotLocationResponse])
def get_spots(db: Session = Depends(get_db), limit: int = 100, search: Optional[str] = ""):
    '''Returns a list of spots'''
    select_stmt = select(
        models.SpotLocation
    )

    if search:
        select_stmt = select_stmt.where(models.SpotLocation.name.like(f"%{search}%"))
    
    select_stmt = select_stmt.limit(limit)

    spots = db.execute(select_stmt).all()

    if not spots:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="no spots found")

    spots_list = []
    for row in spots:
        spots_list.append(row[0])

    return spots_list

@router.get("/spots/find_closest")
def get_closest_spot(lat: float, lng: float, dist: float = 50, db: Session = Depends(get_db)):
    '''Get the closest surf spot to a given lat & lng'''
    print(f"lat: {lat}, lng: {lng}, dist: {dist}")
    spots = db.query(models.SpotLocation).all()
    
    if not spots:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="no surf spots found")

    best = []
    for spot in spots:
        spot_distance = distance.distance((lat, lng), (spot.latitude, spot.longitude)).miles
        if spot_distance < dist:
            best.append({"id": spot.id, "name": spot.name, "subregion_name": spot.subregion_name, "distance": spot_distance, "latitude": spot.latitude, "longitude": spot.longitude})
    sorted_best = sorted(best, key=lambda k: k['distance'])
    
    if not sorted_best:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="surf data not available for this location")
    
    return sorted_best

@router.get("/spots/geojson")
def get_spots_geojson(db: Session = Depends(get_db)):
    '''Get a list of all locations for geojson.'''
    locations = db.query(models.SpotLocation).all()
    geojson_features = []
    geojson_list = {
        "type": "FeatureCollection",
        "features": geojson_features
    }
    for row in locations:
        feature_object = spot_location.SpotLocation(row).get_geojson()
        geojson_features.append(feature_object)
    
    if not geojson_list["features"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="no spots found")

    return geojson_list

@router.get("/spots/{spot_id}", response_model=SpotLocationResponse)
def get_spot_instance(spot_id: str, db: Session = Depends(get_db)):
    '''Get a spot by id'''
    spot = db.query(models.SpotLocation).filter(models.SpotLocation.id == spot_id).first()

    if not spot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"spot id {spot_id} not found")
    
    return spot

@router.get("/locations/geojson")
def get_locations_geojson(db: Session = Depends(get_db)):
    '''Get a list of all locations for geojson'''
    locations = db.query(models.BuoyLocation).filter(models.BuoyLocation.active == True).all()
    geojson_features = []
    geojson_list = {
        "type": "FeatureCollection",
        "features": geojson_features
    }
    for row in locations:
        feature_object = buoy_location.BuoyLocation(row).get_geojson()
        geojson_features.append(feature_object)
    
    if not geojson_list["features"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="no locations found")

    return geojson_list

@router.get("/locations", response_model=List[BuoyLocationResponse])
def get_locations(db: Session = Depends(get_db), limit: int = 100, search: Optional[str] = ""):
    filters = [models.BuoyLocation.active == True]
    select_stmt = select(
        models.BuoyLocation, models.TideStationBuoyLocation.station_id
        ).select_from(
            models.BuoyLocation
        ).join(
            models.TideStationBuoyLocation, models.BuoyLocation.location_id == models.TideStationBuoyLocation.location_id, isouter=True
        ).filter(
            *filters
        ).order_by(
            models.BuoyLocation.weight.desc()
        )

    if search:
        select_stmt = select_stmt.where(models.BuoyLocation.name.like(f"%{search}%"))
    
    select_stmt = select_stmt.limit(limit)
    location = db.execute(select_stmt).all()

    locations_list = []
    for row in location:
        row[0].station_id = row[1]
        locations_list.append(row[0])

    return locations_list

@router.get("/locations/{location_id}", response_model=BuoyLocationResponse)
def get_location(location_id: str, db: Session = Depends(get_db)):
    '''Get by location_id'''
    select_stmt = select(
        models.BuoyLocation, models.TideStationBuoyLocation.station_id
    ).select_from(
        models.BuoyLocation
    ).join(
        models.TideStationBuoyLocation, models.BuoyLocation.location_id == models.TideStationBuoyLocation.location_id, isouter=True
    ).where(
        models.BuoyLocation.location_id == location_id
    ).order_by(
        models.BuoyLocation.weight.desc()
    ).limit(1)

    location = db.execute(select_stmt).all()

    if not location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"location id {location_id} not found")
    
    location_result = location[0]
    location_result[0].station_id = location_result[1]
    return location_result[0]

# TODO rename this to something else - "spots" is being used for location of surf spots, not user favs
@router.get("/locations/spots/count")
def count_locations(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    spots = db.query(
        func.count(models.UserLocation.user_id)
    ).where(
        models.UserLocation.user_id == current_user.id
    ).group_by(
        models.UserLocation.location_id, models.UserLocation.user_id
    ).count()
    return {"count": spots}

# Deprecated - use /locations/{location_id}/latest-observation instead
@router.get("/locations/{location_id}/latest", response_model=BuoyLocationNOAASummary)
def get_location(location_id: str, db: Session = Depends(get_db)):
    '''get latest wave summary for this location id'''
    location_summary = db.query(
        models.BuoyLocationNoaaSummary
    ).filter(
        models.BuoyLocationNoaaSummary.location_id == location_id,
    ).order_by(
        models.BuoyLocationNoaaSummary.timestamp.desc()
    ).first()
    if not location_summary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"location {location_id} not found")
    return location_summary

@router.get("/locations/{location_id}/latest-observation", response_model=List[BuoyLocationLatestObservation], response_model_exclude_none=True)
def get_location_latest_observation(location_id: str):
    '''get latest observation for this location id'''
    buoy_data = buoy.BuoyLatestObservation(location_id)
    
    try:
        r = httpx.get(buoy_data.url())
        r.raise_for_status()
        data = buoy_data.parse_latest_reading_data(r.text)
        return data
    except httpx.RequestError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"An error occurred while requesting {exc.request.url!r}.")
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail="Not found")

# should be an admin only route - add later
@router.post("/locations", status_code=status.HTTP_201_CREATED, response_model=BuoyLocationResponse)
def create_location(location: BuoyLocationPost, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    '''Create a location & return the new location'''
    if current_user.is_admin == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    new_location = models.BuoyLocation(**location.dict())
    db.add(new_location)
    try:
        db.commit()
        db.refresh(new_location)
    except:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="something went wrong, please try again")
    
    return new_location

# should be an admin only route - add later
@router.delete("/locations/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_location(id: str, db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    '''Delete a location'''
    location_query = db.query(models.BuoyLocation).filter(models.BuoyLocation.id == id)
    location = location_query.first()

    if location == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"location '{id}' not found")

    if current_user.is_admin == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    # consider sync strategy here
    location_query.delete()
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# should be an admin only route - add later
@router.put("/locations/{id}", response_model=BuoyLocationResponse)
def update_location(id: int, updated_location: BuoyLocationPut, db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    '''update a location based on location id'''
    query = db.query(models.BuoyLocation).filter(models.BuoyLocation.id == id)
    current_location = query.first()

    if current_location == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"location id: {id} not found")

    if current_user.is_admin == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    query.update(updated_location.dict(exclude_unset=True), synchronize_session=False)
    db.commit()
    return query.first()
