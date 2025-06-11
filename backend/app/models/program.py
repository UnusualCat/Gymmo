from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class Program(Base):
    __tablename__ = "programs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    google_drive_file_id = Column(String, unique=True, index=True)
    sheet_name = Column(String, default="Programmi") 
    
    # Relationships
    users = relationship("User", secondary="user_program", back_populates="programs")
    workouts = relationship("Workout", back_populates="program")

class Workout(Base):
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("programs.id"))
    week_number = Column(Integer)
    day_number = Column(Integer)
    exercise_name = Column(String)
    series = Column(String)
    repetitions = Column(String)
    rest_time = Column(String)
    notes = Column(String)
    extra_notes = Column(String)
    progression = Column(String)
    video_url = Column(String)
    
    # Relationships
    program = relationship("Program", back_populates="workouts") 