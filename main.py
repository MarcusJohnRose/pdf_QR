from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from models.models import Base
from models.database import engine
from pathlib import Path
from routes import api
import os
from services.settings import Settings as settingsService
from routes import settings as settings_route

app = FastAPI()

app.include_router(api.router)
app.include_router(settings_route.router)
# Static files
app.mount("/", StaticFiles(directory=os.path.join(Path(__file__).parent , "frontend"), html=True), name="static")

# Setup DB
Base.metadata.create_all(bind=engine)
settingsService.init_settings()

# Ensure folders exist
Path("uploads").mkdir(exist_ok=True)
Path("processed_pdfs").mkdir(exist_ok=True)

# Register routes
