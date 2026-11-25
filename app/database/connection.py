from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker




# SQLite database URL
DATABASE_URL = "sqlite:///./helpdesk.db"


# Create database engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)


# Create session factory
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


# Database dependency
def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()