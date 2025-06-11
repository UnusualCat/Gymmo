from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import Program, User
from ..routers.users import get_current_user

router = APIRouter(tags=["programs"])

@router.post("/{program_id}/assign")
def assign_program_to_user(
    program_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verifica se il programma esiste
    program = db.query(Program).filter(Program.id == program_id).first()
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Programma non trovato"
        )
    
    # Assegna il programma all'utente
    if program not in current_user.programs:
        current_user.programs.append(program)
        db.commit()
    
    return {"message": "Programma assegnato con successo"}

@router.get("/my-programs")
def get_user_programs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return [
        {
            "id": program.id,
            "name": program.name,
            "google_drive_file_id": program.google_drive_file_id
        }
        for program in current_user.programs
    ] 