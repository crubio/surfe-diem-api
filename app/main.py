'''main app module'''
from . import models
from .database import engine
from fastapi import FastAPI
from .routers import location, user, auth, forecast, tides, weather, batch
# from .routers import user_location  # Commented out for review
from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=engine)

app = FastAPI(docs_url=None, redoc_url="/api/v1")

# configure this for a specific web app if we want to close down the API.
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# grabs the router obj from appropriate file
app.include_router(location.router)
app.include_router(forecast.router)
app.include_router(tides.router)
app.include_router(user.router)
app.include_router(auth.router)
# app.include_router(user_location.router)  # Commented out for review
app.include_router(weather.router)
app.include_router(batch.router)

# path operation (route) decorator
@app.get("/")
def root():
    '''docstring'''
    return {"message": "hello from surfe-diem"}