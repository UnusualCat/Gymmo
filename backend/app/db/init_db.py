import logging
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.db.base import Base
from backend.app.db.session import engine
from backend.app.core.security import get_password_hash
from backend.app.models import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db(db: Session) -> None:
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create admin user
    user = db.query(User).filter(User.email == "admin@example.com").first()
    if not user:
        user = User(
            email="admin@example.com",
            hashed_password=get_password_hash("admin"),
            is_admin=True,
        )
        db.add(user)
        db.commit()
        logger.info("Created admin user")
    else:
        logger.info("Admin user already exists") 