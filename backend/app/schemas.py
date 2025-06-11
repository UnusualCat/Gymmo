from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    is_admin: bool

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class WorkoutProgramBase(BaseModel):
    name: str
    description: str
    duration: int
    level: str

class WorkoutProgramCreate(WorkoutProgramBase):
    pass

class WorkoutProgram(WorkoutProgramBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True 