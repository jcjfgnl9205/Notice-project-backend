from typing import List, Optional

from ..models import Notices, Users
from .schemas import NoticeList, Notice, NoticeCreate, NoticeUpdate
from ..utils import notice_crud
from ..users.auth import get_logged_in_user, get_user

from fastapi import APIRouter, Depends, HTTPException, Response, status
from db.connection import get_db
from sqlalchemy.orm import Session
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException

from fastapi_pagination import Page, paginate, add_pagination

router = APIRouter(
    prefix="/notices",
    tags=["notices"],
    responses={404: {"descriptions": "Not found"}}
)


# Notice List
@router.get("/", response_model=Page[NoticeList])
async def read_all_by_notice(page: Optional[int] = 0, db: Session = Depends(get_db)):
    notices =notice_crud.get_notices(db=db)
    response = [ notice.__dict__ for notice in notices ]
    return paginate(response)

add_pagination(router)

# Notice List Count
@router.get("/cnt")
async def read_all_by_notice_cnt(db: Session = Depends(get_db)):
    notices = notice_crud.get_notices(db=db)
    print(notices)
    return len(notices)

# Notice Create
@router.post("/create", response_model=NoticeCreate)
async def create_notice(notice: NoticeCreate
                            , Authorize: AuthJWT = Depends()
                            , db: Session = Depends(get_db)):

    current_user = Authorize.get_jwt_subject()
    user = db.query(Users).filter(Users.username == current_user).first()

    if not user or not user.is_staff:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="権限がありません。")

    return notice_crud.create_notice(db=db, notice=notice, owner_id=user.id).__dict__

# Notice Read
@router.get("/{notice_id}", response_model=Notice)
async def read_by_notice(notice_id: int, db: Session = Depends(get_db)):
    notice = notice_crud.get_notice(db=db, notice_id=notice_id)
    if not notice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    response = Notice(
        title = notice.title,
        content = notice.content,
        user = {"username": notice.username, "is_active": notice.is_active}
    )
    return response


# Notice Delete
@router.delete("/{notice_id}")
async def delete_notice(notice_id: int
                        , user: dict = Depends(get_logged_in_user)
                        , db: Session = Depends(get_db)):

    if not notice_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid notice id")

    user_id = get_user(username=user['current_user'], db=db).id
    notice = db.query(Notices).filter(Notices.owner_id == user_id).filter(Notices.id == notice_id).first()
    if not notice:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad Request")

    return notice_crud.delete_notice(db=db, notice_id=notice_id)


# Notice Update
@router.put("/{notice_id}", response_model=Notice)
async def update_notice(notice_id: int
                        , notice: NoticeUpdate
                        , user: dict = Depends(get_logged_in_user)
                        , db: Session = Depends(get_db)):
    if not notice_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid notice id")

    user_id = get_user(username=user['current_user'], db=db).id
    db_notice = db.query(Notices).filter(Notices.owner_id == user_id).filter(Notices.id == notice_id).first()
    if not db_notice:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad Request")

    return notice_crud.update_notice(db=db, notice_id=notice_id, owner_id=user_id, notice=notice)
