from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, validator
from ..users.schemas import UserBase


class NoticeBase(BaseModel):
    title: str
    content: str
    views: int = 0
    created_at: datetime = None
    updated_at: datetime = None

class NoticeList(NoticeBase):
    id: int

class CommentBase(BaseModel):
    comment: str
    created_at: datetime = None
    updated_at: datetime = None

class CommentCreate(CommentBase):
    notice_id: int

    @validator('created_at', pre=True, always=True)
    def set_created_at_now(cls, v):
        return v or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    @validator('updated_at', pre=True, always=True)
    def set_updated_at_now(cls, v):
        return v or datetime.now().strftime('%Y-%m-%d %H:%M:%S')

class Comment(CommentBase):
    id: int
    username: str
    owner_id: int

class Notice(NoticeBase):
    id: int
    user: UserBase
    like_cnt: int
    hate_cnt: int
    comment: Optional[List[Comment]] = []

    class Config:
        orm_mode = True


class NoticeCreate(NoticeBase):

    @validator('created_at', pre=True, always=True)
    def set_created_at_now(cls, v):
        return v or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    @validator('updated_at', pre=True, always=True)
    def set_updated_at_now(cls, v):
        return v or datetime.now().strftime('%Y-%m-%d %H:%M:%S')

class NoticeUpdate(NoticeBase):
    pass
