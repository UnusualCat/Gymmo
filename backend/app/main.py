from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, users, programs, admin
from .database import engine, SessionLocal
from .models import Base, User
from .routers.auth import get_password_hash

# Create database tables
Base.metadata.create_all(bind=engine)

# Create admin user if it doesn't exist
def init_admin():
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.email == "admin@gymmo.com").first()
        if not admin:
            admin = User(
                email="admin@gymmo.com",
                name="Admin",
                hashed_password=get_password_hash("admin123"),
                is_active=True,
                is_admin=True
            )
            db.add(admin)
            db.commit()
            print("Admin user created successfully!")
            print("Email: admin@gymmo.com")
            print("Password: admin123")
    except Exception as e:
        print(f"Error creating admin user: {e}")
    finally:
        db.close()

# Initialize admin user
init_admin()

app = FastAPI(title="Gymmo API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(programs.router, prefix="/api/programs", tags=["programs"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])

@app.get("/")
def read_root():
    return {"message": "Benvenuto nell'API di Gymmo"} 