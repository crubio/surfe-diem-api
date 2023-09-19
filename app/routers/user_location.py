from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy.exc import DBAPIError, SQLAlchemyError
from .. import schemas, database, models, oauth2
from ..schemas import UserLocation
from ..database import get_db

router = APIRouter(
    prefix="/api/v1",
    tags=["User_Locations"]
)

@router.post("/favorites", status_code=status.HTTP_201_CREATED)
def toggle_user_location(location: UserLocation, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    '''favorite or unfavorite this user_id / location_id combo'''
    # check that location id exists first
    location_query = db.query(models.BuoyLocation).filter(models.BuoyLocation.id == location.location_id)
    existing_location = location_query.first()

    if not existing_location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    # check if this relation already exists
    favorite_query = db.query(models.UserLocation).filter(
        models.UserLocation.location_id == existing_location.id,
        models.UserLocation.user_id == current_user.id
    )

    favorite_exists = favorite_query.first()

    if location.direction == 1:
        if favorite_exists:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT)
        new_favorite = models.UserLocation(user_id=current_user.id, location_id=location.location_id)
        db.add(new_favorite)
        db.commit()
        return {"message": "successfully added"}
    else:
        if not favorite_exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        favorite_query.delete(synchronize_session=False)
        db.commit()
        return {"message": "successfully removed"}
