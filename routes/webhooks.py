from fastapi import APIRouter, Request, HTTPException
import stripe # type: ignore
from sqlalchemy.orm import Session
from database import get_db
from models import User, Subscription
from fastapi import FastAPI, Depends, HTTPException

router = APIRouter()

# Stripe webhook secret
WEBHOOK_SECRET = "your_webhook_secret"

@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, WEBHOOK_SECRET)
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle events
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user = db.query(User).filter(User.email == session["customer_email"]).first()
        if user:
            subscription = Subscription(
                user_id=user.id,
                stripe_subscription_id=session["subscription"],
                status="active"
            )
            user.is_subscribed = True
            db.add(subscription)
            db.commit()

    return {"status": "success"}
