import os
from dotenv import load_dotenv

from ..models import Users
from .schemas import UserCreate, UserSelect, UserLogin, Token
from passlib.context import CryptContext
from typing import Optional
from db.connection import get_db
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer

load_dotenv()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES")

class User(BaseModel):
    username: str
    password: str

class Settings(BaseModel):
    authjwt_secret_key: str = os.getenv("JWT_SECRET_KEY")

@AuthJWT.load_config
def get_config():
    return Settings()

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={401:{"user": "Not authorized"}}
)

# passwordをhashする
def get_password_hash(password: str):
    return password_context.hash(password)

# passwordが保存されているhashと一致するかチェックする
def verify_password(plain_password, hashed_password):
    return password_context.verify(plain_password, hashed_password)

# userを認証してreturnする
def authenticate_user(db, username: str, password: str):
    user = db.query(Users).filter(Users.username == username).first()

    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

# Login
@router.post("/login")
async def login(user: UserLogin, Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):

    # DBに登録されているユーザーを確認する
    db_user = authenticate_user(db, user.username, user.password)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="usernameまたはpasswordが間違います。")

    access_token = Authorize.create_access_token(subject=user.username)
    refresh_token = Authorize.create_refresh_token(subject=user.username)

    return {"access_token": access_token, "refresh_token": refresh_token}

# Loginしているユーザー
@router.get("/protected")
async def get_logged_in_user(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
        
    except Exception as e:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    current_user = Authorize.get_jwt_subject()
    return {"current_user": current_user}


# 新しいaccess_tokenを生成する
@router.get("/new_token")
async def create_new_token(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_refresh_token_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    current_user = Authorize.get_jwt_subject()
    access_token = Authorize.create_access_token(subject=current_user)

    return {"new_access_token": access_token}

# ユーザーの新規登録
@router.post("/register")
async def register_user(user: UserCreate
                        , Authorize: AuthJWT = Depends()
                        , db: Session = Depends(get_db)):
    
    validation1 = db.query(Users).filter(Users.username == user.username).first()
    validation2 = db.query(Users).filter(Users.email == user.email).first()

    if validation1 is not None:
        raise HTTPException(status_code=400, detail="IDが既に存在します。")
    if validation2 is not None:
        raise HTTPException(status_code=400, detail="Emailが既に存在します。")

    user_model = Users(
        email = user.email,
        username = user.username,
        hashed_password = get_password_hash(user.password),
        first_name = user.first_name,
        last_name = user.last_name,
        is_active = True,
        is_staff = False
    )
    db.add(user_model)
    db.commit()
    
    access_token = Authorize.create_access_token(subject=user.username)
    refresh_token = Authorize.create_refresh_token(subject=user.username)

    return {"access_token": access_token, "refresh_token": refresh_token}
