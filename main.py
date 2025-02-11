from fastapi import FastAPI, Depends, HTTPException, APIRouter,Request, Response
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
import models
from automation import run_every_two_weeks
import stripe # type: ignore
import os
from database import get_db,Base,engine
from starlette import status
from typing import Annotated
from schemas import CheckoutRequest,CheckoutResponse,ChangePasswordRequest
import auth
import secrets
import email_helper


# Initialize database
Base.metadata.create_all(bind=engine)

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")  # Secure API Key

router = APIRouter()

import crud
import schemas
from database import get_db

app = FastAPI()
app.include_router(auth.router)


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
@app.post("/create-checkout-session/", response_model=CheckoutResponse)
def create_checkout_session(request: CheckoutRequest, db: Session = Depends(get_db)):
    """Creates a Stripe Checkout Session for one-time payments."""

    # ✅ Fetch user from database
    user = db.query(models.User).filter(models.User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        # ✅ Create a Stripe customer if not already set
        if not user.stripe_customer_id:
            customer = stripe.Customer.create(
                email=user.email,
                name=user.username
            )
            user.stripe_customer_id = customer.id
            db.commit()  # ✅ Save customer ID in DB

        # ✅ Create a Stripe Checkout Session
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="subscription",
            customer=user.stripe_customer_id,
            line_items=[
                {
                    "price": "price_1Qpq2UKjuXgzFbXkJ7ywbLTK",  
                    "quantity": 1,
                }
            ],
            metadata={"user_id": request.user_id}, 
            success_url="http://localhost:5173/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="http://localhost:5173/cancel",
        )


        existing_subscription = db.query(models.Subscription).filter(
            models.Subscription.user_id == request.user_id
        ).first()

        if existing_subscription:
            existing_subscription.checkout_session_id = session.id
            existing_subscription.status = "pending"  # Reset status
        else:
            new_subscription = models.Subscription(
                user_id=request.user_id,
                checkout_session_id=session.id,
                status="pending"
            )
            db.add(new_subscription)

        db.commit()

        return {"session_url": session.url}

    except stripe.error.StripeError as e:  # ✅ Handle Stripe-specific errors
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")
    


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[Dict, Depends(auth.get_current_user)]
# login 
@app.get("/",status_code=status.HTTP_200_OK)
async def user(user:user_dependency,db:db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user

    

    # Handling of stripe webhook 
  
STRIPE_SECRET = "whsec_2659890a063d46e3d08b474fddc6c89960e65a4bac35879befb917565bd307ec"


@app.post("/webhook/")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("Stripe-Signature", "")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_SECRET)  # Replace with your actual webhook secret
    except stripe.error.SignatureVerificationError:
        return {"error": "Invalid signature"}, 400

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = session["metadata"]["user_id"]
        checkout_session_id = session["id"]
        stripe_subscription_id = session.get("subscription")

        print(f"✅ Checkout Completed: User {user_id}, Subscription ID {stripe_subscription_id}")

        user = db.query(models.User).filter(models.User.id == user_id).first()
        if user:
            # ✅ Create or update subscription
            subscription = db.query(models.Subscription).filter(models.Subscription.user_id == user_id).first()
            if not subscription:
                subscription = models.Subscription(user_id=user_id, checkout_session_id=checkout_session_id)
                db.add(subscription)
            print('------------------------------Subscription ID-------------------------')
            print(subscription.stripe_subscription_id)
            subscription.stripe_subscription_id = stripe_subscription_id
            subscription.status = "active"
            user.is_subscribed = True
            user.subscription_status = "active"

            db.commit()

    elif event["type"] == "invoice.payment_failed":
        invoice = event["data"]["object"]
        stripe_subscription_id = invoice["subscription"]

        print(f"❌ Payment Failed: Subscription {stripe_subscription_id}")

        subscription = db.query(models.Subscription).filter(models.Subscription.stripe_subscription_id == stripe_subscription_id).first()
        if subscription:
            user = db.query(models.User).filter(models.User.id == subscription.user_id).first()
            if user:
                user.subscription_status = "past_due"
                user.is_subscribed = False  # ✅ Mark as unsubscribed
                db.commit()

    elif event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        stripe_subscription_id = subscription["id"]

        print(f"🚫 Subscription Canceled: {stripe_subscription_id}")

        subscription = db.query(models.Subscription).filter(models.Subscription.stripe_subscription_id == stripe_subscription_id).first()
        if subscription:
            user = db.query(models.User).filter(models.User.id == subscription.user_id).first()
            if user:
                user.subscription_status = "canceled"
                user.is_subscribed = False
                db.delete(subscription)  # ✅ Delete subscription record
                db.commit()

    return {"status": "success"}


# get user subscription status
@app.get("/subscription_status/{user_id}/")
async def get_subscription_status(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        return {"subscription_status": user.subscription_status, "is_subscribed": user.is_subscribed}
    else:
        raise HTTPException(status_code=404, detail="User not found")
    

# Update user profile
@app.put("/user/update/", response_model=schemas.UserResponse)
def update_user(
    user_update: schemas.UserUpdate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Update user profile."""
    user = db.query(models.User).filter(models.User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_update.username:
        user.username = user_update.username
    if user_update.email:
        user.email = user_update.email

    db.commit()
    db.refresh(user)
    return user

# Password reste

@app.post("/user/reset-password")
def reset_password(token: str, new_password: str, db: Session = Depends(get_db)):
    """Reset password using a token."""
    user = db.query(models.User).filter(models.User.reset_token == token).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid token")

    user.password = auth.hash_password(new_password)
    user.reset_token = None 
    db.commit()

    return {"message": "Password reset successful"}


# handle email sending for password reset
 

@app.post("/user/reset-password-request")
def request_password_reset(email: str, db: Session = Depends(get_db)):
    """Generate password reset token and send email."""
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    reset_token = secrets.token_urlsafe(32)  # Generate token
    user.reset_token = reset_token
    db.commit()

    reset_link = f"http://localhost:5173/reset-password?token={reset_token}"
    email_helper.send_email(user.email, "Password Reset", f"Click here to reset your password: {reset_link}")
    
    return {"message": "Reset email sent"}


# Change the password 

@app.put("/user/change-password")
def change_password(
    request: ChangePasswordRequest,  # Accept JSON body
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Change user password."""
    user = db.query(models.User).filter(models.User.id == current_user.id).first()
    
    if not user or not auth.verify_password(request.current_password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect current password")
    
    user.password = auth.hash_password(request.new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}
# 🔹 Delete User
@app.delete("/user/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully!"}


# 🔹 Get User by ID
@app.get("/user/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
