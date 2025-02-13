from fastapi import FastAPI, HTTPException, Depends,APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from typing import Annotated
from pydantic import BaseModel
from starlette import status
from jose import JWTError, jwt # type: ignore
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from models import User
from database import SessionLocal
from sqlalchemy.orm import Session
from database import get_db

load_dotenv()

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    
)

#1 Secret key for JWT
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30



#2 .Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

#3. Create pydnatic model for user
class UserIn(BaseModel):
    username: str
    password: str
    email: str

class UserOut(BaseModel):
    access_token: str
    token_type: str
    userId:int




@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserIn, db: Session = Depends(get_db)):
    print(f"Received request: {user}")  # Debugging: Print received data

    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    create_user_model = User(
        email=user.email,
        username=user.username,
        password=pwd_context.hash(user.password),
        is_subscribed=False,
    )
    db.add(create_user_model)
    db.commit()
    db.refresh(create_user_model)

    return {"message": "User created successfully"}

   


# Hash password
def hash_password(password: str):
    return pwd_context.hash(password)

# Verify password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# # Generate JWT token
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# # Authenticate user
def authenticate_user(username: str, password: str, db):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if user and verify_password(password, user.password):
        return user
    return None

# # Get current user from token
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        # Decode the token to get user info
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id = payload.get("id")

        if username is None or user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Query the user from the database using the user_id or username
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        # Return the user object
        return user

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


db_dependency = Annotated[Session, Depends(get_db)]

# # User login endpoint
@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)
):
    print(f"Received login request: username={form_data.username}, password={form_data.password}")

    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token(data={"sub": user.username, "id": user.id}, expires_delta=timedelta(minutes=30))
    
    return {"access_token": token, "token_type": "bearer", "userId": user.id, "is_subscribed":user.is_subscribed}

# # Protected route (only accessible to logged-in users)
# @app.get("/protected")
# async def protected_route(current_user: dict = Depends(get_current_user)):
#     return {"message": f"Hello {current_user['username']}! This is a protected route."}


# # User registration endpoint
# @app.post("/register")
# def register(username: str, password: str):
#     if username in fake_users_db:
#         raise HTTPException(status_code=400, detail="Username already taken")
#     fake_users_db[username] = {
#         "username": username,
#         "hashed_password": hash_password(password),
#     }
#     return {"message": "User registered successfully"}
