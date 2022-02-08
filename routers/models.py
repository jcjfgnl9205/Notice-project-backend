from sqlalchemy import ForeignKey, Boolean, Column, Integer, String, DateTime
from db.session import Base, metadata, engine
from sqlalchemy.orm import relationship


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=False)
    is_staff = Column(Boolean, default=False)

    notices = relationship("Notices", back_populates="owner")
    comment = relationship("Comments", back_populates="owner")
    notice_like = relationship("NoticeLike", back_populates="owner")

class Notices(Base):
    __tablename__ = "notices"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(String)
    views = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("Users", back_populates="notices")
    notice_file = relationship("NoticeFile", back_populates="notice")
    comment = relationship("Comments", back_populates="notice")
    notice_like = relationship("NoticeLike", back_populates="notice")

class NoticeFile(Base):
    __tablename__ = "notice_file"
    
    id = Column(Integer, primary_key=True, index=True)
    path = Column(String)
    file_name = Column(String)
    file_size = Column(Integer)
    file_type = Column(Integer)
    file_download = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    notice_id = Column(Integer, ForeignKey("notices.id"))

    notice = relationship("Notices", back_populates="notice_file")

class Comments(Base):
    __tablename__ = "notice_comment"

    id = Column(Integer, primary_key=True, index=True)
    comment = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    owner_id = Column(Integer, ForeignKey("users.id"))
    notice_id = Column(Integer, ForeignKey("notices.id"))

    owner = relationship("Users", back_populates="comment")
    notice = relationship("Notices", back_populates="comment")

class NoticeLike(Base):
    __tablename__ = "notice_like"

    id = Column(Integer, primary_key=True, index=True)
    like = Column(Integer, default=False)
    hate = Column(Integer, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    notice_id = Column(Integer, ForeignKey("notices.id"))

    owner = relationship("Users", back_populates="notice_like")
    notice = relationship("Notices", back_populates="notice_like")

metadata.create_all(bind=engine)
