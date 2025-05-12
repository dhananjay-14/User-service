from sqlite3 import IntegrityError
from typing import List, Optional
from fastapi import HTTPException,status
from sqlalchemy.orm import Session
from app.common.errors.errors import DuplicateEntity, EntityNotFound
from app.models.userModel import User
from app.modules.auth.token.token import hash_password
from app.modules.users.schemas.userSchema import RoleEnum, UserCreate, UserUpdate
from sqlalchemy import func, or_, and_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

# Retrieve all users from the database
def get_users(db: Session) -> list[User]:
    try:
        return db.query(User).all()
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching users"
        )


# Retrieve a single user by their ID, or raise 404 if not found
def get_user(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise EntityNotFound('User')
    return user


# Create a new user, hashing their password and handling duplicates
def create_user(db: Session, user_in: UserCreate, creator_role: RoleEnum) -> User:
    data = user_in.model_dump()
    # Only superadmin may assign roles other than 'user'
    if creator_role is not RoleEnum.superadmin:
        data["role"] = RoleEnum.user
    data["hashed_password"] = hash_password(data.pop("password"))
    db_user = User(**data)
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise DuplicateEntity("User", "email")
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(500, "Error creating user")


# Update an existing user with validation and authorization checks
def update_user(db: Session, target_id: int, updater_id: int, updater_role: RoleEnum, user_in: UserUpdate) -> User:
    db_user = get_user(db, target_id)
    # Authorization:
    if updater_role == RoleEnum.user:
        # users can only update themselves
        if updater_id != target_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Users can only update their own profile")
    elif updater_role == RoleEnum.admin:
        # admins can update themselves and users only
        if updater_id != target_id and db_user.role != RoleEnum.user:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Admins can only update users with role 'user'")

    data = user_in.model_dump()
    if(user_in.password):
        data["hashed_password"] = hash_password(data.pop("password"))

    for field, val in data.items():
        if val is not None:
            setattr(db_user, field, val)
    try:
        db.commit()
        db.refresh(db_user)
        return db_user
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(500, "Error updating user")


# Delete a user by ID (only superadmin allowed)
def delete_user(db: Session, target_id: int, deleter_role: RoleEnum) -> None:
    if deleter_role is not RoleEnum.superadmin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only superadmin can delete users")
    try:
        db_user = get_user(db, target_id)
        db.delete(db_user)
        db.commit()
    except EntityNotFound:
        raise
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting user"
        )
    

# Search users with optional filters for names, email, gender, and IP
def search_users(
    db: Session,
    first_name: Optional[str] = None,
    last_name:  Optional[str] = None,
    email:      Optional[str] = None,
    gender:     Optional[str] = None,
    ip_address: Optional[str] = None,
) -> List[User]:
    try:
        filters = []
        if first_name:
            filters.append(User.first_name.ilike(f"%{first_name}%"))
        if last_name:
            filters.append(User.last_name.ilike(f"%{last_name}%"))
        if email:
            filters.append(User.email.ilike(f"%{email}%"))
        if gender:
            filters.append(func.lower(User.gender) == gender.lower())
        if ip_address:
            filters.append(User.ip_address == ip_address)

        query = db.query(User)
        if filters:
            query = query.filter(and_(*filters))

        return query.all()
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error searching users"
        )