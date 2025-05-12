from sqlalchemy.orm import Session
from app.models.userModel import User
from app.modules.auth.token.token import hash_password, verify_password
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.common.db.session import get_db
from app.modules.auth.token.token import decode_access_token
from app.modules.users.schemas.userSchema import RoleEnum

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")
router = APIRouter(tags=["Auth"])

# Authenticates user with email and password, returns User object if valid
def authenticate_user(db: Session, email: str, password: str) -> User:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


# Creates new user account with hashed password
def register_user(db: Session, user_data: dict) -> User:
    user_data["hashed_password"] = hash_password(user_data.pop("password"))
    user = User(**user_data)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# Validates JWT token and returns current authenticated user
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = decode_access_token(token)
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception
    user = db.query(User).get(user_id)
    if not user:
        raise credentials_exception
    return user


# Dependency that checks if user has required role
def require_role(*allowed: RoleEnum):
    def dep(user = Depends(get_current_user)):
        if user.role not in allowed:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
        return user
    return dep