from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SETTINGS_DB_URL = "sqlite:///./settings.db"

engine = create_engine(SETTINGS_DB_URL, connect_args={"check_same_thread": False})
SessionLocalSettings = sessionmaker(autocommit=False, autoflush=False, bind=engine)

