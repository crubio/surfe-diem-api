from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy import DateTime, JSON, UniqueConstraint, Enum
from .database import Base

class Test(Base):
    __tablename__ = "test"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)

class BuoyLocation(Base):
    __tablename__ = "buoy_location"
    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    url = Column(String)
    description = Column(String)
    location = Column(String)
    active = Column(Boolean, default=True, nullable=False)
    date_created = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())
    date_updated = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now(), onupdate=func.now())
    weight = Column(Integer, default=0, nullable=False)

class BuoyLocationNoaaSummary(Base):
    __tablename__ = "locations_noaa_summary"

    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(String, ForeignKey("buoy_location.location_id", ondelete="SET NULL"), nullable=True)
    timestamp = Column(String)
    date_created = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())
    wvht = Column(String)
    precipitation = Column(String)
    wind = Column(String)
    gust = Column(String)
    peak_period = Column(String)
    water_temp = Column(String)
    swell = Column(String)
    period = Column(String)
    direction = Column(String)
    wind_wave = Column(String)
    ww_period = Column(String)
    ww_direction = Column(String)

class BuoyLocationLatestObservation(Base):
    __tablename__ = "locations_latest_observation"
    id = Column(Integer, primary_key=True, nullable=False)
    location_id = Column(String, ForeignKey("buoy_location.location_id", ondelete="SET NULL"), nullable=True)
    date_created = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())
    timestamp = Column(String)
    title = Column(String)
    href = Column(String)
    published = Column(String)
    location = Column(String)
    wind_speed = Column(String)
    dominant_wave_period = Column(String)
    dew_point = Column(String)
    water_temp = Column(String)
    mean_wave_direction = Column(String)
    wind_gust = Column(String)
    average_period = Column(String)
    wind_direction = Column(String)
    air_temp = Column(String)
    atmospheric_pressure = Column(String)
    significant_wave_height = Column(String)

class TideStation(Base):
    __tablename__ = "tide_stations"
    id = Column(Integer, primary_key=True, nullable=False)
    station_id = Column(String, unique=True, nullable=False)
    station_name = Column(String)
    latitude = Column(String)
    longitude = Column(String)

# deprecated, do not use
class TideStationBuoyLocation(Base):
    __tablename__ = "tide_station_buoy_location"
    id = Column(Integer, primary_key=True, nullable=False)
    station_id = Column(String, ForeignKey("tide_stations.station_id", ondelete="CASCADE"), nullable=True)
    location_id = Column(String, ForeignKey("buoy_location.location_id", ondelete="CASCADE"), nullable=True)

class SpotLocation(Base):
    __tablename__ = "spot_location"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, unique=True, nullable=False)
    timezone = Column(String)
    latitude = Column(String)
    longitude = Column(String)
    subregion_name = Column(String)
    slug = Column(String, unique=True, nullable=False)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    is_admin = Column(Boolean, server_default='FALSE')
    date_created = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())

class UserLocation(Base):
    __tablename__ = "user_location"
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    location_id = Column(Integer, ForeignKey("buoy_location.location_id", ondelete="CASCADE"), primary_key=True)

# SpotAccuracyRating model for spot_accuracy_rating table
class SpotAccuracyRating(Base):
    __tablename__ = "spot_accuracy_rating"
    id = Column(Integer, primary_key=True, autoincrement=True)
    spot_id = Column(Integer, nullable=False)
    spot_slug = Column(String(128), nullable=False)
    rating = Column(Enum('accurate', 'not_accurate', name='spot_rating_enum'), nullable=False)
    forecast_json = Column(JSON, nullable=True)
    timestamp = Column(DateTime, nullable=False)
    session_id = Column(String(128), nullable=False)
    ip_address = Column(String(45), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    __table_args__ = (
        UniqueConstraint('spot_id', 'session_id', 'ip_address', 'timestamp', name='uq_spot_session_ip_date'),
    )
