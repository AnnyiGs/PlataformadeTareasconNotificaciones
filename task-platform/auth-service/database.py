from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Read DB configuration from environment variables (set by docker-compose)
MYSQL_USER = os.getenv("DB_USER", "root")
MYSQL_PASSWORD = os.getenv("DB_PASSWORD", "root")
# In docker-compose the service name is `mysql`; fall back to `db_mysql` for compatibility
MYSQL_HOST = os.getenv("DB_HOST", os.getenv("MYSQL_HOST", "mysql"))
MYSQL_PORT = os.getenv("DB_PORT", os.getenv("MYSQL_TCP_PORT", "3306"))
MYSQL_DB = os.getenv("DB_NAME", "tasks_db")

DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"

# Configure SQLAlchemy engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
