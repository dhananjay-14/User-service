from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.common.config.config import settings

# Create engine with stringified URL
engine = create_engine(str(settings.database_url))

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

def get_db():
    """
    Dependency to get DB session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
