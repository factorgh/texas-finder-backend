from fastapi import FastAPI, Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
import models
from automation import run_every_two_weeks
import stripe # type: ignore
import os
from database import get_db
from models import User, Subscription
from schemas import CheckoutRequest,CheckoutResponse

router = APIRouter()

import crud
import schemas
from database import engine, Base, get_db

app = FastAPI()


# Run cron job
run_every_two_weeks()


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Create county
@app.post("/counties/", response_model=schemas.County)
def create_county(county: schemas.CountyCreate, db: Session = Depends(get_db)):
    return crud.create_county(db=db, county=county)

# Get all counties
@app.get("/counties/", response_model=List[schemas.County])
def get_counties(db: Session = Depends(get_db)):
    return crud.get_counties(db=db)

# Get county by ID
@app.get("/counties/{county_id}", response_model=Optional[schemas.County])
def get_county(county_id: int, db: Session = Depends(get_db)):
    county = crud.get_county_by_id(db=db, county_id=county_id)
    if county is None:
        raise HTTPException(status_code=404, detail="County not found")
    return county

# Create operator
@app.post("/operators/", response_model=schemas.Operator)
def create_operator(operator: schemas.OperatorCreate, db: Session = Depends(get_db)):
    return crud.create_operator(db=db, operator=operator)

# Get all operators
@app.get("/operators/", response_model=List[schemas.Operator])
def get_operators(db: Session = Depends(get_db)):
    return crud.get_operators(db=db)

# Get operator by ID
@app.get("/operators/{operator_id}", response_model=Optional[schemas.Operator])
def get_operator(operator_id: int, db: Session = Depends(get_db)):
    operator = crud.get_operator_by_id(db=db, operator_id=operator_id)
    if operator is None:
        raise HTTPException(status_code=404, detail="Operator not found")
    return operator

# Create lease
@app.post("/leases/", response_model=schemas.Lease)
def create_lease(lease: schemas.LeaseCreate, county_id: int, operator_id: int, db: Session = Depends(get_db)):
    return crud.create_lease(db=db, lease=lease, county_id=county_id, operator_id=operator_id)

# Get all leases
@app.get("/leases/", response_model=List[schemas.Lease])
def get_leases(db: Session = Depends(get_db)):
    return crud.get_leases(db=db)

# Get lease by ID
@app.get("/leases/{lease_id}", response_model=Optional[schemas.Lease])
def get_lease(lease_id: int, db: Session = Depends(get_db)):
    lease = crud.get_lease_by_id(db=db, lease_id=lease_id)
    if lease is None:
        raise HTTPException(status_code=404, detail="Lease not found")
    return lease




# STATISTICS ONLY
@app.get("/summary")
def get_statistics(db: Session = Depends(get_db)):
    # Counting the total number of permits
    total_permits = db.query(func.count(models.Permit.id)).scalar()

    # Counting the total number of operators
    total_operators = db.query(func.count(models.Operator.id)).scalar()

    # Counting the total number of leases
    total_leases = db.query(func.count(models.Lease.id)).scalar()

    return {
        "total_permits": total_permits,
        "total_operators": total_operators,
        "total_leases": total_leases
    }


# Stripe payment and subscription

# Set your Stripe secret key

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")  # Secure API Key

router = APIRouter()

@router.post("/create-checkout-session", response_model=CheckoutResponse)
def create_checkout_session(request: CheckoutRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        # ✅ Optional: Check if user already has a Stripe customer ID
        if not user.stripe_customer_id:
            customer = stripe.Customer.create(
                email=user.email,
                name=user.full_name
            )
            user.stripe_customer_id = customer.id
            db.commit()  # ✅ Save customer ID in DB

        # ✅ Create a Stripe Checkout Session
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="subscription",
            customer=user.stripe_customer_id,  # ✅ Assign user to Stripe customer
            line_items=[
                {
                    "price": request.price_id,  # Stripe `price_id`
                    "quantity": 1,
                }
            ],
            metadata={"user_id": request.user_id},  # ✅ Track user for webhook
            success_url="http://localhost:5173/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="http://localhost:5173/cancel",
        )

        # ✅ Save Subscription in Database
        new_subscription = Subscription(
            user_id=request.user_id,
            stripe_subscription_id=session.id,
            status="pending"
        )
        db.add(new_subscription)
        db.commit()

        return {"session_url": session.url}

    except Exception as e:
        db.rollback()  # ✅ Prevent partial commits
        raise HTTPException(status_code=400, detail=str(e))
