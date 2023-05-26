from typing import List

from fastapi import Depends, FastAPI, HTTPException, Response, status, APIRouter
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, utils
from ..schemas import (UserCreate, UserResponse)

router = APIRouter(
    prefix="/api/v1",
    tags=["Users"]
)

@router.post("/users", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # hash the password
    hashed_pw = utils.hash(user.password)
    user.password = hashed_pw

    new_user =  models.User(**user.dict())
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except:
        # this is generic for now, but assuming the user already exists and a db error bubbled up
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="something went wrong, please try again later.")
    return new_user

@router.get("/users/{id}", response_model=UserResponse)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user with id {id} does not exist")
    
    return user.first()