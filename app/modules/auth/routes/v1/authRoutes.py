from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.common.db.session import get_db
from app.modules.auth.schemas.authSchemas import Token
from app.modules.auth.token.token import create_access_token
from app.modules.auth.user.userAuth import authenticate_user
from app.modules.users.repositories import usersRepo as repositories
from app.modules.users.schemas.userSchema import RoleEnum, UserCreate, UserOut
from app.common.notifications.notification import manager

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")
router = APIRouter(tags=["Auth"])

# Endpoint to authenticate user and generate JWT token
# Accepts username and password, returns access token
@router.post("/token", response_model=Token)
def login_for_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    access_token = create_access_token({"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}


# Endpoint to register new user
# Creates user with 'user' role and broadcasts creation event
@router.post("/sign-up", response_model=UserOut)
async def create_user(
    user: UserCreate, 
    db: Session = Depends(get_db),
):
    user = repositories.create_user(db, user,RoleEnum.user)
    # Emit right after creation:
    await manager.broadcast_event({
        "type": "created",
        "user": UserOut.from_orm(user).dict()
    })
    return user
