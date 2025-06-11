from sqlalchemy import Column, Integer, String, Boolean, Table, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

    # Relationships
    programs = relationship("Program", secondary="user_program", back_populates="users")

# Tabella di associazione per la relazione many-to-many tra User e Program
user_program = Table(
    "user_program",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("program_id", Integer, ForeignKey("programs.id"))
) 