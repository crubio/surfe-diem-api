from typing import List, Union, Optional
import httpx
import re

from fastapi import Depends, HTTPException, Response, status, APIRouter
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from geopy import distance
from unidecode import unidecode

from ..database import get_db
from .. import models, oauth2
from ..schemas import (BuoyLocationNOAASummary, BuoyLocationPost, BuoyLocationResponse, BuoyLocationPut, BuoyLocationLatestObservation, SpotLocationResponse, SpotLocationPost)
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
def get_spots(db: Session = Depends(get_db), limit: int = 500, search: Optional[str] = ""):
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
    spots = db.query(models.SpotLocation).all()
    
    if not spots:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="no surf spots found")

    best = []
    for spot in spots:
        spot_distance = distance.distance((lat, lng), (spot.latitude, spot.longitude)).miles
        if spot_distance < dist:
            best.append({"id": spot.id, "name": spot.name, "subregion_name": spot.subregion_name, "distance": spot_distance, "latitude": spot.latitude, "longitude": spot.longitude, "slug": spot.slug})
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
        feature_object = spot_location.SpotLocation.from_obj(row).get_geojson()
        geojson_features.append(feature_object)
    
    if not geojson_list["features"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="no spots found")

    return geojson_list

@router.get("/spots/{spot_id}", response_model=SpotLocationResponse)
def get_spot_instance(spot_id: str, db: Session = Depends(get_db)):
    '''Get a spot by id or slug'''
    # Try to find by ID first (numeric)
    if spot_id.isdigit():
        spot = db.query(models.SpotLocation).filter(models.SpotLocation.id == int(spot_id)).first()
    else:
        # If not numeric, try to find by slug
        spot = db.query(models.SpotLocation).filter(models.SpotLocation.slug == spot_id).first()

    if not spot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"spot {spot_id} not found")
    
    return spot

@router.get("/spots/slug/{slug}", response_model=SpotLocationResponse)
def get_spot_by_slug(slug: str, db: Session = Depends(get_db)):
    '''Get a spot by slug explicitly'''
    spot = db.query(models.SpotLocation).filter(models.SpotLocation.slug == slug).first()

    if not spot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"spot with slug '{slug}' not found")
    
    return spot

def generate_slug(name: str) -> str:
    """Generate a URL-friendly slug from spot name."""
    slug = unidecode(name).lower()
    slug = re.sub(r'[^a-zA-Z0-9]+', '-', slug)
    slug = re.sub(r'^[-]+|[-]+$', '', slug)  # Remove leading/trailing hyphens
    slug = re.sub(r'[-]{2,}', '-', slug)     # Remove consecutive hyphens
    return slug

def generate_unique_slug(name: str, db: Session) -> str:
    """Generate a unique slug, adding numbers if needed to avoid conflicts."""
    base_slug = generate_slug(name)
    slug = base_slug
    counter = 1
    
    while db.query(models.SpotLocation).filter(models.SpotLocation.slug == slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    return slug

@router.post("/spots", status_code=status.HTTP_201_CREATED, response_model=SpotLocationResponse)
def create_spot(spot: SpotLocationPost, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    '''Create a new surf spot with automatic slug generation'''
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    # Generate unique slug
    slug = generate_unique_slug(spot.name, db)
    
    # Create new spot with slug
    new_spot = models.SpotLocation(
        name=spot.name,
        timezone=spot.timezone,
        latitude=spot.latitude,
        longitude=spot.longitude,
        subregion_name=spot.subregion_name,
        slug=slug
    )
    
    db.add(new_spot)
    try:
        db.commit()
        db.refresh(new_spot)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to create spot: {str(e)}")
    
    return new_spot

@router.get("/locations/find_closest")
def get_closest_location(lat: float, lng: float, limit = 3, dist: float = 100, db: Session = Depends(get_db)):
    '''Get the closest buoy location to a given lat & lng'''
    locations = db.query(models.BuoyLocation).filter(models.BuoyLocation.active == True).all()
    
    best = []
    for buoy in locations:
        coords = buoy_location.BuoyLocation.from_obj(buoy).parse_location()
        buoy_distance = distance.distance((lat, lng), (coords[1], coords[0])).miles
        if buoy_distance < dist:
            # get latest observation for this buoy
            latest_obs = get_latest_obvservation(buoy.location_id) or None
            best.append(
                {
                    "location_id": buoy.location_id,
                    "name": buoy.name,
                    "url": buoy.url,
                    "description": buoy.description,
                    "location": buoy.location,
                    "distance": buoy_distance,
                    "latitude": coords[1], 
                    "longitude": coords[0],
                    "latest_observation": latest_obs,
                }
            )

    sorted_best = sorted(best, key=lambda k: k['distance'])
    sorted_best = sorted_best[:limit]
    if not sorted_best:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="surf data not available for this location")
    
    return sorted_best

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
        feature_object = buoy_location.BuoyLocation.from_obj(row).get_geojson()
        geojson_features.append(feature_object)
    
    if not geojson_list["features"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="no locations found")

    return geojson_list

@router.get("/locations", response_model=List[BuoyLocationResponse])
def get_locations(db: Session = Depends(get_db), limit: int = 500, search: Optional[str] = ""):
    filters = [models.BuoyLocation.active == True]
    select_stmt = select(
        models.BuoyLocation
        ).select_from(
            models.BuoyLocation
        ).filter(
            *filters
        ).order_by(
            models.BuoyLocation.weight.desc()
        )

    if search:
        select_stmt = select_stmt.where(models.BuoyLocation.name.like(f"%{search}%"))
    
    select_stmt = select_stmt.limit(limit)
    location = db.execute(select_stmt).all()

    if not location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="no locations found")
    locations_list = []
    for row in location:
        locations_list.append(row[0])
    return locations_list

@router.get("/locations/{location_id}", response_model=BuoyLocationResponse)
def get_location(location_id: str, db: Session = Depends(get_db)):
    '''Get by location_id'''
    select_stmt = select(
        models.BuoyLocation
    ).select_from(
        models.BuoyLocation
    ).where(
        models.BuoyLocation.location_id == location_id
    ).order_by(
        models.BuoyLocation.weight.desc()
    ).limit(1)

    location = db.execute(select_stmt).all()

    if not location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"location id {location_id} not found")
    
    location_result = location[0]
    return location_result[0]

# TODO rename this to something else - "spots" is being used for location of surf spots, not user favs
# @router.get("/locations/spots/count")
# def count_locations(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
#     spots = db.query(
#         func.count(models.UserLocation.user_id)
#     ).where(
#         models.UserLocation.user_id == current_user.id
#     ).group_by(
#         models.UserLocation.location_id, models.UserLocation.user_id
#     ).count()
#     return {"count": spots}

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

def get_latest_obvservation(location_id: str):
    buoy_data = buoy.BuoyLatestObservation(location_id)

    try:
        r = httpx.get(buoy_data.url(), timeout=5.0)
        r.raise_for_status()
        if r.status_code != 200:
            return None
    except Exception as e:
        print(f"Error fetching data for {location_id}: {str(e)}")
        return None
    
    try:
        data = buoy_data.parse_latest_reading_data(r.text)
        return data
    except Exception as e:
        print(f"Error parsing data for {location_id}: {str(e)}")
        return None

@router.get("/locations/{location_id}/latest-observation", response_model_exclude_none=True)
def get_location_latest_observation(location_id: str):
    '''get latest observation for this location id'''
    latest_observation_data = get_latest_obvservation(location_id)
    if not latest_observation_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"location {location_id} not found")
    return latest_observation_data

@router.get("/locations/{location_id}/realtime")
def get_location(location_id: str, limit: int = 10, send_html: bool = False):
    '''
    get realtime from ndbc.noaa.gov/data/realtime2/{station_id}.txt
    '''
    base_url = "https://www.ndbc.noaa.gov/data/realtime2/"
    url = base_url + location_id + ".txt"
    try:
        r = httpx.get(url)
        r.raise_for_status()
    except httpx.RequestError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"location {location_id} not found")
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"location {location_id} invalid id")

    if not r.text:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"location {location_id} not found")

    data = r.text.splitlines()
    del data[0:2]  # remove the first two lines which are headers

    buoy_real_time = buoy_location.BuoyDataBuilder().build(location_id, data)

    if buoy_real_time.data.empty:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"location {location_id} not found")
    
    if send_html:
        df_html = buoy_real_time.get_data().to_html(classes='table table-striped table-hover', index=False)
    else:
        df_html = None
    
    return {
        "location_id": buoy_real_time.location_id,
        "url": buoy_real_time.url,
        "data": buoy_real_time.data.head(limit),
        "html": df_html
    }

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
