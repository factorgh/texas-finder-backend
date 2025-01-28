from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from . import database, schemas, crud

app = FastAPI()

# Dependency to get the DB session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/counties/", response_model=schemas.County)
def create_county(county: schemas.CountyCreate, db: Session = Depends(get_db)):
    return crud.create_county(db=db, county=county)

@app.post("/operators/", response_model=schemas.Operator)
def create_operator(operator: schemas.OperatorCreate, db: Session = Depends(get_db)):
    return crud.create_operator(db=db, operator=operator)

@app.post("/leases/", response_model=schemas.Lease)
def create_lease(lease: schemas.LeaseCreate, county_id: int, operator_id: int, db: Session = Depends(get_db)):
    return crud.create_lease(db=db, lease=lease, county_id=county_id, operator_id=operator_id)

@app.get("/counties/", response_model=List[schemas.County])
def get_counties(db: Session = Depends(get_db)):
    return crud.get_counties(db=db)

@app.get("/operators/", response_model=List[schemas.Operator])
def get_operators(db: Session = Depends(get_db)):
    return crud.get_operators(db=db)

@app.get("/leases/", response_model=List[schemas.Lease])
def get_leases(db: Session = Depends(get_db)):
    return crud.get_leases(db=db)
