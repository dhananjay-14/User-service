import pandas as pd
import psycopg2
from sqlalchemy.orm import Session
from app.common.db.session import SessionLocal,engine
from app.common.db.base    import Base
from app.models.userModel import User
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.modules.auth.token.token import hash_password

CSV_FILE_PATH = "./app/mock_data.csv"
DEFAULT_PLAIN_PASSWORD = "ChangeMe123!"

#Import users from CSV file to the database
def import_users():
    # Recreate tables in dev
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    df = pd.read_csv(CSV_FILE_PATH)
    db: Session = SessionLocal()

    for _, row in df.iterrows():
        # build the ORM model args
        user = User(
            first_name      = row["first_name"],
            last_name       = row["last_name"],
            email           = row["email"],
            gender          = row["gender"],
            ip_address      = row["ip_address"],
            role            = "user",
            hashed_password = hash_password(DEFAULT_PLAIN_PASSWORD),
        )
        try:
            db.add(user)
            db.commit()
            print(f"Imported: {user.email} (id={user.id})")
        except IntegrityError as e:
            db.rollback()
            # psycopg2 error codes: UNIQUE_VIOLATION is '23505'
            pgcode = getattr(e.orig, 'pgcode', None)
            if pgcode == psycopg2.errorcodes.UNIQUE_VIOLATION:
                print(f"[Duplicate] {row['email']}")
            else:
                print(f"[IntegrityError:{pgcode}] inserting {row['email']}: {e.orig}")
        except SQLAlchemyError as e:
            db.rollback()
            print(f"[SQLAlchemyError] {row['email']}: {e}")
        except Exception as e:
            db.rollback()
            print(f"[Exception] {row['email']}: {e}")

    db.close()

if __name__ == "__main__":
    import_users()