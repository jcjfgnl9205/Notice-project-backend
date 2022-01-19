import os
from dotenv import load_dotenv

from .models import Users
from .schemas import UserCreate, UserSelect, UserLogin, Token
from typing import Optional
from db.connection import get_db
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from starlette.responses import RedirectResponse
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi.responses import HTMLResponse

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES")

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={401:{"user": "Not authorized"}}
)

class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.username: Optional[str] = None
        self.password: Optional[str] = None
        
    async def create_oauth_form(self):
        form = await self.request.form()
        self.username = form.get("username")
        self.password = form.get("password")

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

# 新しいtoken生成する
def create_access_token(username: str, user_id:int, expires_delta: Optional[timedelta] = None):
    encode = {"username":username, "user_id": user_id}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    encode.update({"exp": expire})
    encoded_jwt = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# tokenをdecodeしてuserをreturnする
# tokenが無効になるとHttpExceptionをreturnする
async def get_current_user(request: Request):
    try:
        token = request.cookies.get("access_token")
        if token is None:
            return None
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        user_id: int = payload.get("user_id")
        print(username)
        print(user_id)
        if username is None or user_id is None:
            logout(request)
        return {"username": username, "user_id": user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="tokenが無効です")


# tokenの時間設定
# JWTtokenを生成してreturnする
@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()
                                , db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="usernameまたはpasswordが間違います。")
    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(user.username, user.id, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


# Login
@router.post("/login", response_model=Token)
async def login(user: UserLogin, response: Response
                , db: Session = Depends(get_db)):
    try:
        validate_user_cookie = await login_for_access_token(user, db=db)

        if not validate_user_cookie:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="usernameまたはpasswordが間違います。")
        return {"access_token": validate_user_cookie["access_token"], "token_type": "bearer"}
    except HTTPException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="error")


# ユーザーの新規登録
@router.post("/register", response_model=UserSelect)
async def register_user(user: UserCreate
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
        is_active = True
    )
    db.add(user_model)
    db.commit()

    return { **user.dict() }
