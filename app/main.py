from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi_pagination import add_pagination
from slowapi import Limiter
from app.common.config.config import settings
from app.common.db.base import Base
from app.common.db.session import engine
from app.modules.users.routes.v1.users import router as users_router
from app.modules.auth.routes.v1.authRoutes import router as auth_router
from sqlalchemy.exc import IntegrityError
from app.common.errors.errors import EntityNotFound, DuplicateEntity
import app.common.utils.logger as logger
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi import Limiter, _rate_limit_exceeded_handler

limiter = Limiter(key_func=get_remote_address)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)


# Register the exception handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Exception handlers
@app.exception_handler(IntegrityError)
async def sqlalchemy_integrity_error_handler(request: Request, exc: IntegrityError):
    # Handle unique constraint violations
    detail = str(exc.orig)
    return JSONResponse(
        status_code=400,
        content={"detail": detail}
    )

@app.exception_handler(EntityNotFound)
async def entity_not_found_handler(request: Request, exc: EntityNotFound):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(DuplicateEntity)
async def duplicate_entity_handler(request: Request, exc: DuplicateEntity):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


# Include module routers
app.include_router(
    auth_router,
    prefix="/api/v1/auth",
    tags=["Auth"],
)

app.include_router(
    users_router,
    prefix="/api/v1/users",
    tags=["Users"],
)

# Enable pagination
add_pagination(app)