from .models import Users
from .schemas import UserCreate, UserSelect
from db.connection import get_db
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi import APIRouter, Depends, HTTPException

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={401:{"user": "Not authorized"}}
)


def get_password_hash(password: str):
    return password_context.hash(password)

# ユーザーの新規登録
@router.post("/register", response_model=UserSelect)
async def register_user(user: UserCreate
                        , db: Session = Depends(get_db)):
    
    validation1 = db.query(Users).filter(Users.username == user.username).first()
    validation2 = db.query(Users).filter(Users.email == user.email).first()

    if user.password != user.password2:
        raise HTTPException(status_code=400, detail="Passwordを確認してください。")
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
