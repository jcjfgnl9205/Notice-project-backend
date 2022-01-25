from typing import List, Optional

from ..models import Notices, Users
from .schemas import Notice, NoticeCreate
from ..utils import notice_crud
from ..users.auth import get_logged_in_user

from fastapi import APIRouter, Depends, HTTPException, Response, status
from db.connection import get_db
from sqlalchemy.orm import Session
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException


router = APIRouter(
    prefix="/notices",
    tags=["notices"],
    responses={404: {"descriptions": "Not found"}}
)


# Notice List
@router.get("/", response_model=List[Notice])
async def read_all_by_notice(q: Optional[int] = 100, db: Session = Depends(get_db)):
    return notice_crud.get_notices(db=db, skip=0, limit=100)

# Notice Create
@router.post("/create", response_model=Notice)
async def create_notice(notice: NoticeCreate
                            , Authorize: AuthJWT = Depends()
                            , db: Session = Depends(get_db)):

    current_user = Authorize.get_jwt_subject()
    user = db.query(Users).filter(Users.username == current_user).first()

    if not user or not user.is_staff:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="権限がありません。")

    return notice_crud.create_notice(db=db, notice=notice, owner_id=user.id)

# Notice Read
@router.get("/{notice_id}", response_model=Notice)
async def read_by_notice(notice_id: int, db: Session = Depends(get_db)):
    return notice_crud.get_notice(db=db, notice_id=notice_id)
