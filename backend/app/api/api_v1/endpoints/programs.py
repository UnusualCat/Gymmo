from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.api import deps
from backend.app.models import User
from backend.app.models import Program
from backend.app.schemas import Program as ProgramSchema
from backend.app.schemas import ProgramCreate, ProgramUpdate
from backend.app.services.workout import process_program

router = APIRouter()

@router.get("/", response_model=List[ProgramSchema])
def read_programs(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve programs.
    """
    if current_user.is_admin:
        programs = db.query(Program).offset(skip).limit(limit).all()
    else:
        programs = current_user.programs
    return programs

@router.post("/", response_model=ProgramSchema)
def create_program(
    *,
    db: Session = Depends(deps.get_db),
    program_in: ProgramCreate,
    current_user: User = Depends(deps.get_current_admin_user),
) -> Any:
    """
    Create new program.
    """
    program = Program(**program_in.dict())
    db.add(program)
    db.commit()
    db.refresh(program)
    return program

@router.put("/{id}", response_model=ProgramSchema)
def update_program(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    program_in: ProgramUpdate,
    current_user: User = Depends(deps.get_current_admin_user),
) -> Any:
    """
    Update a program.
    """
    program = db.query(Program).filter(Program.id == id).first()
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    
    for field, value in program_in.dict(exclude_unset=True).items():
        setattr(program, field, value)
    
    db.add(program)
    db.commit()
    db.refresh(program)
    return program

@router.get("/{id}", response_model=ProgramSchema)
def read_program(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get program by ID.
    """
    program = db.query(Program).filter(Program.id == id).first()
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    if not current_user.is_admin and program not in current_user.programs:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return program

@router.delete("/{id}", response_model=ProgramSchema)
def delete_program(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: User = Depends(deps.get_current_admin_user),
) -> Any:
    """
    Delete a program.
    """
    program = db.query(Program).filter(Program.id == id).first()
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    db.delete(program)
    db.commit()
    return program

@router.post("/{id}/process", response_model=ProgramSchema)
def process_program_file(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: User = Depends(deps.get_current_admin_user),
) -> Any:
    """
    Process program's Excel file and update workouts.
    """
    program = db.query(Program).filter(Program.id == id).first()
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    
    process_program(db, program)
    return program

@router.post("/{id}/users/{user_id}", response_model=ProgramSchema)
def add_user_to_program(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    user_id: int,
    current_user: User = Depends(deps.get_current_admin_user),
) -> Any:
    """
    Add a user to a program.
    """
    program = db.query(Program).filter(Program.id == id).first()
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user not in program.users:
        program.users.append(user)
        db.add(program)
        db.commit()
        db.refresh(program)
    
    return program

@router.delete("/{id}/users/{user_id}", response_model=ProgramSchema)
def remove_user_from_program(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    user_id: int,
    current_user: User = Depends(deps.get_current_admin_user),
) -> Any:
    """
    Remove a user from a program.
    """
    program = db.query(Program).filter(Program.id == id).first()
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user in program.users:
        program.users.remove(user)
        db.add(program)
        db.commit()
        db.refresh(program)
    
    return program 