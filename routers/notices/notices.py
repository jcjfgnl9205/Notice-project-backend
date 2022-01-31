from typing import List, Optional

from ..models import Notices, Users, Comments
from .schemas import NoticeList, Notice, NoticeCreate, NoticeUpdate, CommentCreate
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
    notices = notice_crud.get_notices(db=db)
    response = [ notice.__dict__ for notice in notices ]
    return paginate(response)

add_pagination(router)

# Notice Create
@router.post("/", response_model=NoticeCreate)
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

    return notice_crud.response_notice(db=db, notice_id=notice_id)


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


# Notice Comment Create
@router.post("/{notice_id}/comment", response_model=Notice)
async def create_notice_comment(notice_id: int
                                , comment: CommentCreate
                                , user: dict = Depends(get_logged_in_user)
                                , db: Session = Depends(get_db)):
    
    if not comment.notice_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid notice id")

    create = notice_crud.create_notice_comments(db=db, comment=comment, owner_id=user.id)
    if create["status"] != 200:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad Request")

    return notice_crud.response_notice(db=db, notice_id=notice_id)


# Notice Comment Delete
@router.delete("/{notice_id}/comment/{comment_id}", response_model=Notice)
async def delete_notice_comment(notice_id: int
                                , comment_id: int
                                , user: dict = Depends(get_logged_in_user)
                                , db: Session = Depends(get_db)):
    if not notice_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid notice id")

    notice = db.query(Notices).filter(Notices.id == notice_id).first()
    if not notice:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad Request")

    comment = notice_crud.get_comment(db=db, comment_id=comment_id, owner_id=user.id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad Request")

    return notice_crud.delete_comment(db=db, notice_id=notice_id, comment_id=comment_id)
