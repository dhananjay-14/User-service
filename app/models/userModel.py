from sqlalchemy import Column, Integer, String, Index, Enum as SQLEnum
from app.common.db.base import Base
from app.modules.users.schemas.userSchema import RoleEnum

class User(Base):
    """SQLAlchemy User model for users table.

    Stores user data including personal info, auth details, and role.
    Includes composite index on name fields and unique email constraint.
    """
    __tablename__ = "users"

    id         = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True, nullable=False)
    last_name  = Column(String, index=True, nullable=False)
    email      = Column(String, unique=True, index=True, nullable=False)
    gender     = Column(String, index=True, nullable=False)
    ip_address = Column(String, index=True, nullable=False)
    hashed_password = Column(String, nullable=False) 
    role            = Column(SQLEnum(RoleEnum), default=RoleEnum.user, nullable=False, index=True)

    # A composite index as first name and last name will be mostly used together
    __table_args__ = (
        Index("ix_users_name", "first_name", "last_name"),
    )

