import os
from typing import List, Optional
from datetime import datetime
from ..models import Notices, Users, Comments
from .schemas import NoticeList, Notice, NoticeCreate, NoticeUpdate, CommentCreate, CommentBase, Comment, NoticeFile, NoticeFileCreate
from ..utils import notice_crud
from ..users.auth import get_logged_in_user, get_user

from fastapi import APIRouter, Depends, HTTPException, Response, status, File, UploadFile, Form
from fastapi.responses import FileResponse
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

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE_DIR = os.path.join(BASE_DIR, 'static', 'files')

# Notice List
@router.get("/", response_model=Page[NoticeList])
async def read_all_by_notice(page: Optional[int] = 0, db: Session = Depends(get_db)):
    notices = notice_crud.get_notices(db=db)
    response = [ notice.__dict__ for notice in notices ]
    return paginate(response)


# Notice Create
@router.post("/", response_model=Notice)
async def create_notice(title: str=Form(...)
                        , content: str=Form(...)
                        , files: Optional[List[UploadFile]] = File(...)
                        , Authorize: AuthJWT = Depends()
                        , db: Session = Depends(get_db)):
    current_user = Authorize.get_jwt_subject()
    user = db.query(Users).filter(Users.username == current_user).first()

    if not user or not user.is_staff:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="権限がありません。")

    notice = NoticeCreate(title=title, content=content)
    db_notice = notice_crud.create_notice(db=db, notice=notice, owner_id=user.id, files=files)

    for file in files:
        if file.filename == '':
            continue
        contents = await file.read()
        f_name = '-'.join([datetime.now().strftime("%y%m%d_%H%M%S"), file.filename])
        with open(os.path.join(FILE_DIR, f_name), "wb") as fp:
            fp.write(contents)
        f = NoticeFileCreate(path='/'.join([FILE_DIR, f_name]),
                             file_name=file.filename, 
                             file_size=os.path.getsize(FILE_DIR+'/'+f_name), 
                             file_type=file.content_type, 
                             notice_id=db_notice.id)
        notice_crud.create_notice_file(db=db, notice_file=f)

    return notice_crud.response_notice(db=db, notice_id=db_notice.id)

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

    notice = db.query(Notices).filter(Notices.owner_id == user.id).filter(Notices.id == notice_id).first()
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
@router.post("/{notice_id}/comment", response_model=Page[Comment])
async def create_notice_comment(notice_id: int
                                , comment: CommentCreate
                                , user: dict = Depends(get_logged_in_user)
                                , db: Session = Depends(get_db)):
    
    if not comment.notice_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid notice id")

    create = notice_crud.create_notice_comments(db=db, comment=comment, owner_id=user.id)
    if create["status"] != 200:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad Request")

    return paginate(notice_crud.get_comments(db=db, notice_id=notice_id))


# Notice Comment Update
@router.put("/{notice_id}/comment/{comment_id}", response_model=Page[Comment])
async def update_notice_comment(notice_id: int
                                , comment_id: int
                                , comment: CommentBase
                                , user: dict = Depends(get_logged_in_user)
                                , db: Session = Depends(get_db)):
    if not notice_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid notice id")

    is_notice = db.query(Notices).filter(Notices.id == notice_id).first()
    if not is_notice:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad Request")

    is_comment = notice_crud.get_comment(db=db, comment_id=comment_id, owner_id=user.id)
    if not is_comment:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad Request")

    return paginate(notice_crud.update_comment(db=db, notice_id=notice_id, comment_id=comment_id, owner_id=user.id, comment= comment))


# Notice Comment Delete
@router.delete("/{notice_id}/comment/{comment_id}", response_model=Page[Comment])
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

    return paginate(notice_crud.delete_comment(db=db, notice_id=notice_id, comment_id=comment_id))

# Comment paginate
@router.get("/{notice_id}/comment", response_model=Page[Comment])
async def read_all_by_comment(notice_id: int, page: Optional[int] = 0, db: Session = Depends(get_db)):
    comments = notice_crud.get_comments(db=db, notice_id=notice_id)
    return paginate(comments)


# getLike
@router.post("/{notice_id}/getLike")
async def get_like(notice_id: int
                    , user: dict = Depends(get_logged_in_user)
                    , db: Session = Depends(get_db)):
    if not notice_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid notice id")
    return notice_crud.get_notice_like_hate(db=db, notice_id=notice_id, owner_id=user.id)


# Notice Like Button evnet
@router.post("/{notice_id}/like")
async def update_notike_like_cnt(notice_id: int
                                , user: dict = Depends(get_logged_in_user)
                                , db: Session = Depends(get_db)):

    if not notice_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid notice id")

    db_like = notice_crud.get_notice_like_hate(db=db, notice_id=notice_id, owner_id=user.id)
    if not db_like:
        return notice_crud.create_notice_like(db=db, notice_id=notice_id, owner_id=user.id)

    return notice_crud.update_notice_like(db=db, notice_id=notice_id, owner_id=user.id)

# Notice Hate Button evnet
@router.post("/{notice_id}/hate")
async def update_notike_like_cnt(notice_id: int
                                , user: dict = Depends(get_logged_in_user)
                                , db: Session = Depends(get_db)):

    if not notice_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid notice id")

    db_hate = notice_crud.get_notice_like_hate(db=db, notice_id=notice_id, owner_id=user.id)
    if not db_hate:
        return notice_crud.create_notice_hate(db=db, notice_id=notice_id, owner_id=user.id)

    return notice_crud.update_notice_hate(db=db, notice_id=notice_id, owner_id=user.id)


# Notice File Download
@router.get("/file/download/{file_id}")
async def notice_file_download(file_id: int
                                , db: Session = Depends(get_db)):
    f = notice_crud.download_notice_file(db=db, file_id=file_id)
    file_name = f.file_name
    file_path = f.path
    return FileResponse(path=file_path, media_type='application/octet-stream', filename=file_name)


add_pagination(router)
