
from models.appDatabase import SessionLocalSettings as SessionLocal
from models.settings import Setting

from models.appDatabase import engine as appEngine
from models.settings import BaseSettings as settingsBase
from sqlalchemy import select
from datetime import datetime


class Settings:
    DEFAULTS = {
        "qr_code_marker": "#",
        "qr_position": "top-center",
    }

    @staticmethod
    def get_setting_value(key: str, default: str = "") -> str:
        with SessionLocal() as db:
            setting = db.query(Setting).filter(Setting.key == key).first()
            return setting.value if setting else Settings.DEFAULTS.get(key, default)

    @staticmethod
    def init_settings():
        settingsBase.metadata.create_all(bind=appEngine)

        with SessionLocal() as db:
            result = db.execute(select(Setting)).first()
            if not result:
                default_settings = [
                    Setting(key=key, value=value, modified_at=datetime.utcnow())
                    for key, value in Settings.DEFAULTS.items()
                ]
                db.add_all(default_settings)
                db.commit()