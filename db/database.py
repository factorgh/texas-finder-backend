# database.py
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic_settings import BaseSettings

from typing import Any

class Settings(BaseSettings):
    mongodb_uri: str = "mongodb+srv://burchellsbale:Rosemondlamptey@texasfinderdb.3e4pz.mongodb.net/?retryWrites=true&w=majority&appName=texasFinderDb"  
    database_name: str = "counties_db"

    class Config:
        env_file = ".env"  # Optionally use environment variables

settings = Settings()

# Create MongoDB connection
client = AsyncIOMotorClient(settings.mongodb_uri)
database = client[settings.database_name]  # Database used for your project

# Collection reference for County
county_collection = database["counties"]

