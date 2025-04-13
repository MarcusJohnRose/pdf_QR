from sqlalchemy import Column, String, DateTime,Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from datetime import datetime

BaseSettings = declarative_base()

class Setting(BaseSettings):
    __tablename__ = "settings"

    key = Column(String, primary_key=True, index=True)
    value = Column(Text)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
