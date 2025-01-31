from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import database
import crud
import models


app = FastAPI()

# Dependency to get the DB session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/counties/", response_model=models.County)
def create_county(county: models.CountyCreate, db: Session = Depends(get_db)):
    return crud.create_county(db=db, county=county)

@app.post("/operators/", response_model=models.Operator)
def create_operator(operator: models.OperatorCreate, db: Session = Depends(get_db)):
    return crud.create_operator(db=db, operator=operator)

@app.post("/leases/", response_model=models.Lease)
def create_lease(lease: models.LeaseCreate, county_id: int, operator_id: int, db: Session = Depends(get_db)):
    return crud.create_lease(db=db, lease=lease, county_id=county_id, operator_id=operator_id)

@app.get("/counties/", response_model=List[models.County])
def get_counties(db: Session = Depends(get_db)):
    return crud.get_counties(db=db)

@app.get("/operators/", response_model=List[models.Operator])
def get_operators(db: Session = Depends(get_db)):
    return crud.get_operators(db=db)

@app.get("/leases/", response_model=List[models.Lease])
def get_leases(db: Session = Depends(get_db)):
    return crud.get_leases(db=db)

