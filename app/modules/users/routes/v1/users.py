from fastapi import APIRouter, Depends, HTTPException, Request, WebSocket, WebSocketDisconnect
from loguru import logger
from sqlalchemy.orm import Session
from fastapi_pagination import Page, Params, paginate
from app.common.db.session import get_db
from app.models.userModel import User
from app.modules.auth.user.userAuth import get_current_user, require_role
from app.modules.users.schemas.userSchema import RoleEnum, UserOut, UserCreate, UserUpdate
from app.modules.users.repositories import usersRepo as repositories
from app.common.notifications.notification import manager
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

# List users with pagination; accessible by users, admins, and superadmins
@router.get("/list", response_model=Page[UserOut], dependencies=[Depends(require_role(RoleEnum.user, RoleEnum.admin, RoleEnum.superadmin))])
@limiter.limit("100/minute")
def list_users(
    request: Request, 
    params: Params = Depends(),
    db: Session = Depends(get_db),
):
    # Calculate offset and limit based on page and size
    logger.info(f"list_users called by role(s) {params} → page={params.page}, size={params.size}")
    users = repositories.get_users(db)
    return paginate(users, params)


# Search users with optional filters and pagination; restricted to admin/superadmin
@router.get("/search", response_model=Page[UserOut],dependencies=[Depends(require_role(RoleEnum.admin, RoleEnum.superadmin))])
@limiter.limit("50/minute")
def search_users(
    request: Request,
    *,
    params:     Params = Depends(),          
    first_name: str | None = None,
    last_name:  str | None = None,
    email:      str | None = None,
    gender:     str | None = None,
    ip_address: str | None = None,
    db:         Session = Depends(get_db),
):
    """Search users by any combination of fields."""
    logger.info(f"search_users called by role(s) {params} → page={params.page}, size={params.size}")
    users = repositories.search_users(
        db,
        first_name=first_name,
        last_name=last_name,
        email=email,
        gender=gender,
        ip_address=ip_address,
    )
    return paginate(users, params)


# Create a new admin user; only superadmin can perform this action
@router.post("/create-admin", response_model=UserOut, dependencies=[Depends(require_role(RoleEnum.superadmin))])
async def create_user_admin(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    logger.info(f"create_user_admin called with data: {user_data}")
    user= repositories.create_user(db, user_data, creator_role=current_user.role)
    await manager.broadcast_event({
        "type": "created",
        "user": UserOut.from_orm(user).dict()
    })
    return user


# Retrieve a user by ID; accessible by users, admins, and superadmins
@router.get("/{user_id}", response_model=UserOut,dependencies=[Depends(require_role(RoleEnum.user, RoleEnum.admin, RoleEnum.superadmin))])
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
):
    logger.info(f"read_user called with user_id: {user_id}")
    db_user = repositories.get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


# Update an existing user; publishes update event for subscribers
@router.put("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: int, 
    user: UserUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logger.info(f"update_user called for user_id: {user_id} by user: {current_user.id}")
    user = repositories.update_user(db,user_id,current_user.id,current_user.role,user)
    await manager.broadcast_event({
        "type": "updated",
        "user": UserOut.from_orm(user).dict()
    })
    return user

# Delete a user by ID; only superadmin allowed
@router.delete("/{user_id}",dependencies=[Depends(require_role(RoleEnum.superadmin))])
@limiter.limit("10/minute")
async def delete_user(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logger.info(f"delete_user called for user_id: {user_id} by user: {current_user.id}")
    user = repositories.get_user(db, user_id)
    repositories.delete_user(db, user_id, current_user.role)
    await manager.broadcast_event({
        "type": "deleted",
        "user": UserOut.from_orm(user).dict()
    })
    logger.info(f"User {user_id} successfully deleted by user: {current_user.id}")
    return {"ok": True}


# WebSocket endpoint for real-time user notifications via subscribe actions
@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    """
    WebSocket clients should send JSON messages to subscribe:
      {"action":"subscribe_id", "user_id":17}
      {"action":"subscribe_search", "email":"@gmail.com"}
    Then they’ll receive events when matching users are created/updated/deleted.
    """
    await manager.connect(ws)
    try:
        while True:
            msg = await ws.receive_json()
            action = msg.get("action")
            if action == "subscribe_id":
                manager.subscribe_to_id(ws, int(msg["user_id"]))
            elif action == "subscribe_search":
                # remove 'action' key, the rest are filters
                filters = {k: v for k, v in msg.items() if k != "action"}
                manager.subscribe_to_search(ws, filters)
    except WebSocketDisconnect:
        manager.disconnect(ws)