from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.api import deps
from backend.app.core.security import get_password_hash
from backend.app.models import User
from backend.app.schemas import User as UserSchema
from backend.app.schemas import UserCreate, UserUpdate

router = APIRouter()

@router.get("/", response_model=List[UserSchema])
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_admin_user),
) -> Any:
    """
    Retrieve users.
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.post("/", response_model=UserSchema)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
    current_user: User = Depends(deps.get_current_admin_user),
) -> Any:
    """
    Create new user.
    """
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        is_admin=user_in.is_admin,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.put("/{id}", response_model=UserSchema)
def update_user(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    user_in: UserUpdate,
    current_user: User = Depends(deps.get_current_admin_user),
) -> Any:
    """
    Update a user.
    """
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_in.email is not None:
        existing_user = db.query(User).filter(User.email == user_in.email).first()
        if existing_user and existing_user.id != id:
            raise HTTPException(
                status_code=400,
                detail="The user with this email already exists in the system.",
            )
    
    update_data = user_in.dict(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.get("/{id}", response_model=UserSchema)
def read_user(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get user by ID.
    """
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not current_user.is_admin and current_user.id != id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return user

@router.delete("/{id}", response_model=UserSchema)
def delete_user(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: User = Depends(deps.get_current_admin_user),
) -> Any:
    """
    Delete a user.
    """
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return user 