from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import User, Program
from ..routers.users import get_current_user
from ..services.google_drive import drive_service

router = APIRouter(tags=["admin"])

def get_admin_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Non hai i permessi necessari"
        )
    return current_user

@router.get("/users")
def list_users(
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    users = db.query(User).all()
    return [
        {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "is_active": user.is_active,
            "is_admin": user.is_admin,
            "programs": [{"id": p.id, "name": p.name} for p in user.programs]
        }
        for user in users
    ]

@router.get("/programs")
def list_programs(
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    # Ottieni la lista dei file da Google Drive
    drive_files = drive_service.list_files()
    
    # Ottieni i programmi già nel database
    db_programs = db.query(Program).all()
    db_program_ids = {p.google_drive_file_id for p in db_programs}
    
    # Combina i risultati
    return {
        "drive_files": [
            {
                "id": file["id"],
                "name": file["name"],
                "in_database": file["id"] in db_program_ids
            }
            for file in drive_files
        ],
        "database_programs": [
            {
                "id": p.id,
                "name": p.name,
                "google_drive_file_id": p.google_drive_file_id
            }
            for p in db_programs
        ]
    }

@router.post("/programs")
def create_program(
    name: str,
    google_drive_file_id: str,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    # Verifica se il programma esiste già
    existing = db.query(Program).filter(Program.google_drive_file_id == google_drive_file_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Programma già esistente"
        )
    
    # Crea il nuovo programma
    program = Program(
        name=name,
        google_drive_file_id=google_drive_file_id
    )
    db.add(program)
    db.commit()
    db.refresh(program)
    
    return program

@router.post("/users/{user_id}/programs/{program_id}")
def assign_program(
    user_id: int,
    program_id: int,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    # Verifica se l'utente esiste
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utente non trovato"
        )
    
    # Verifica se il programma esiste
    program = db.query(Program).filter(Program.id == program_id).first()
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Programma non trovato"
        )
    
    # Assegna il programma all'utente
    if program not in user.programs:
        user.programs.append(program)
        db.commit()
    
    return {"message": "Programma assegnato con successo"}

@router.delete("/users/{user_id}/programs/{program_id}")
def remove_program(
    user_id: int,
    program_id: int,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    # Verifica se l'utente esiste
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utente non trovato"
        )
    
    # Verifica se il programma esiste
    program = db.query(Program).filter(Program.id == program_id).first()
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Programma non trovato"
        )
    
    # Rimuovi il programma dall'utente
    if program in user.programs:
        user.programs.remove(program)
        db.commit()
    
    return {"message": "Programma rimosso con successo"} 