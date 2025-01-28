# crud.py
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from . import models, database

async def get_county_by_id(county_id: str) -> Optional[models.County]:
    county = await database.county_collection.find_one({"_id": county_id})
    if county:
        return models.County(**county)
    return None

async def get_counties(skip: int = 0, limit: int = 10) -> List[models.County]:
    cursor = database.county_collection.find().skip(skip).limit(limit)
    counties = [models.County(**county) async for county in cursor]
    return counties

async def create_county(county: models.CountyBase) -> models.County:
    county_data = county.dict(exclude_unset=True)
    result = await database.county_collection.insert_one(county_data)
    created_county = await database.county_collection.find_one({"_id": result.inserted_id})
    return models.County(**created_county)
