from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from .database import Base

class Location(Base):
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