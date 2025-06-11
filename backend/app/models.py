from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

    workout_programs = relationship("WorkoutProgram", back_populates="creator")

class WorkoutProgram(Base):
    __tablename__ = "workout_programs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    duration = Column(Integer)  # in weeks
    level = Column(String)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    creator = relationship("User", back_populates="workout_programs") 