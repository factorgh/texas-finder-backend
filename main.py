# main.py
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi import Body
from db import crud, models

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/counties/", response_model=models.County)
async def create_county(county: models.CountyBase):
    created_county = await crud.create_county(county)
    return created_county

@app.get("/counties/", response_model=List[models.County])
async def read_counties(skip: int = 0, limit: int = 10):
    counties = await crud.get_counties(skip=skip, limit=limit)
    return counties

@app.get("/counties/{county_id}", response_model=models.County)
async def read_county(county_id: str):
    county = await crud.get_county_by_id(county_id)
    if not county:
        raise HTTPException(status_code=404, detail="County not found")
    return county
