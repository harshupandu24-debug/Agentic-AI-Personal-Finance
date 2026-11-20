import os
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()
KEY = os.getenv("SECRET_KEY", "development-only-secret")
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(value):
    return pwd.hash(value)

def verify_password(value, hashed):
    return pwd.verify(value, hashed)

def create_token(user_id):
    mins = int(os.getenv("ACCESS_TOKEN_MINUTES", "120"))
    return jwt.encode({"sub": str(user_id), "exp": datetime.utcnow()+timedelta(minutes=mins)}, KEY, algorithm="HS256")

def read_token(token):
    try:
        return int(jwt.decode(token, KEY, algorithms=["HS256"]).get("sub"))
    except (JWTError, TypeError, ValueError):
        return None
