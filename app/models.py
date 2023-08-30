from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from .database import Base

class BuoyLocation(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, nullable=False)
    location_id = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    url = Column(String)
    description = Column(String)
    elevation = Column(String)
    depth = Column(String)
    location = Column(String)
    active = Column(Boolean, server_default='TRUE', nullable=False)
    date_created = Column(TIMESTAMP(timezone=False), nullable=False, server_default=text('now()'))
    date_updated = Column(TIMESTAMP(timezone=False), nullable=False, server_default=text('now()'))
    creator_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

class BuoyLocationNoaaLatest(Base):
    __tablename__ = "locations_noaa_latest"

    id = Column(Integer, primary_key=True, nullable=False)
    location_id = Column(String, ForeignKey("locations.location_id", ondelete="SET NULL"), nullable=True)

class BuoyLocationNoaaHistory(Base):
    __tablename__ = "locations_noaa_history"
    id = Column(Integer, primary_key=True, nullable=False)
    location_id = Column(String, ForeignKey("locations.location_id", ondelete="SET NULL"), nullable=True)

class BuoyLocationNoaaSummary(Base):
    __tablename__ = "locations_noaa_summary"
    id = Column(Integer, primary_key=True, nullable=False)
    location_id = Column(String, ForeignKey("locations.location_id", ondelete="SET NULL"), nullable=True)
    timestamp = Column(String)
    date_created = Column(TIMESTAMP(timezone=False), nullable=False, server_default=text('now()'))
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
    location_id = Column(String, ForeignKey("locations.location_id", ondelete="SET NULL"), nullable=True)
    date_created = Column(TIMESTAMP(timezone=False), nullable=False, server_default=text('now()'))
    timestamp = Column(TIMESTAMP(timezone=False), nullable=False)
    title = Column(String)
    href = Column(String)
    published = Column(TIMESTAMP(timezone=False), nullable=False)
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

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    is_admin = Column(Boolean, server_default='FALSE')
    date_created = Column(TIMESTAMP(timezone=False), nullable=False, server_default=text('now()'))

class UserLocation(Base):
    __tablename__ = "user_location"
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    location_id = Column(Integer, ForeignKey("locations.id", ondelete="CASCADE"), primary_key=True)