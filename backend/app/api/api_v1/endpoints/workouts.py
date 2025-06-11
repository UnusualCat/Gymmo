from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.api import deps
from backend.app.models import User
from backend.app.models import Program, Workout
from backend.app.schemas import Workout as WorkoutSchema
from backend.app.schemas import WorkoutCreate, WorkoutUpdate

router = APIRouter()

@router.get("/", response_model=List[WorkoutSchema])
def read_workouts(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    program_id: int = None,
    week_number: int = None,
    day_number: int = None,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve workouts.
    """
    query = db.query(Workout)
    
    if program_id:
        program = db.query(Program).filter(Program.id == program_id).first()
        if not program:
            raise HTTPException(status_code=404, detail="Program not found")
        if not current_user.is_admin and program not in current_user.programs:
            raise HTTPException(status_code=400, detail="Not enough permissions")
        query = query.filter(Workout.program_id == program_id)
    
    if week_number is not None:
        query = query.filter(Workout.week_number == week_number)
    
    if day_number is not None:
        query = query.filter(Workout.day_number == day_number)
    
    workouts = query.offset(skip).limit(limit).all()
    return workouts

@router.post("/", response_model=WorkoutSchema)
def create_workout(
    *,
    db: Session = Depends(deps.get_db),
    workout_in: WorkoutCreate,
    current_user: User = Depends(deps.get_current_admin_user),
) -> Any:
    """
    Create new workout.
    """
    program = db.query(Program).filter(Program.id == workout_in.program_id).first()
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    
    workout = Workout(**workout_in.dict())
    db.add(workout)
    db.commit()
    db.refresh(workout)
    return workout

@router.put("/{id}", response_model=WorkoutSchema)
def update_workout(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    workout_in: WorkoutUpdate,
    current_user: User = Depends(deps.get_current_admin_user),
) -> Any:
    """
    Update a workout.
    """
    workout = db.query(Workout).filter(Workout.id == id).first()
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    
    for field, value in workout_in.dict(exclude_unset=True).items():
        setattr(workout, field, value)
    
    db.add(workout)
    db.commit()
    db.refresh(workout)
    return workout

@router.get("/{id}", response_model=WorkoutSchema)
def read_workout(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get workout by ID.
    """
    workout = db.query(Workout).filter(Workout.id == id).first()
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    
    program = db.query(Program).filter(Program.id == workout.program_id).first()
    if not current_user.is_admin and program not in current_user.programs:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    return workout

@router.delete("/{id}", response_model=WorkoutSchema)
def delete_workout(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: User = Depends(deps.get_current_admin_user),
) -> Any:
    """
    Delete a workout.
    """
    workout = db.query(Workout).filter(Workout.id == id).first()
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    
    db.delete(workout)
    db.commit()
    return workout 