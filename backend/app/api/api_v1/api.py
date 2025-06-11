from fastapi import APIRouter
from backend.app.api.api_v1.endpoints import auth, users, programs, workouts

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(programs.router, prefix="/programs", tags=["programs"])
api_router.include_router(workouts.router, prefix="/workouts", tags=["workouts"]) 