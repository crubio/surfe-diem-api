from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from .config import settings

from . import schemas, database, models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/login")

# SECRET_KEY
# algorithm
# expiration time

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

def create_access_token(data: dict):
    '''creates jwt'''
    data_to_encode = data.copy()
    expiration_time = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data_to_encode.update({"exp": expiration_time})

    encoded_jwt = jwt.encode(data_to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str, creditials_exception):
    '''verify the token is valid'''
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")

        if user_id is None:
            raise creditials_exception
        token_data = schemas.TokenData(id=str(user_id))
    except JWTError:
        raise creditials_exception

    return token_data

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", 
    headers={"WWW-Authenticate": "Bearer"})

    token = verify_access_token(token, credentials_exception)

    user = db.query(models.User).filter(models.User.id == token.id).first()

    return user
