from fastapi import APIRouter, HTTPException
from fastapi.params import Body
from models.appDatabase import SessionLocalSettings as SessionLocal
from models.settings import Setting
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime
from sqlalchemy import select


router = APIRouter()


class SettingItem(BaseModel):
    key: str
    value: str


@router.get("/settings", response_model=List[SettingItem])
def get_settings():
    with SessionLocal() as db:
        settings = db.query(Setting).all()
        return [SettingItem(key=s.key, value=s.value) for s in settings]


@router.post("/settings/{key}", response_model=SettingItem)
def update_setting(key: str, item: SettingItem):
    with SessionLocal() as db:
        setting = db.query(Setting).filter(Setting.key == key).first()
        if not setting:
            raise HTTPException(status_code=404, detail="Setting not found")

        setting.value = item.value
        setting.modified_at = datetime.utcnow()
        db.commit()
        db.refresh(setting)
        return SettingItem(key=setting.key, value=setting.value)