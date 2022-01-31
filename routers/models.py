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

class Notices(Base):
    __tablename__ = "notices"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(String)
    like_cnt = Column(Integer)
    hate_cnt = Column(Integer)
    views = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("Users", back_populates="notices")
    comment = relationship("Comments", back_populates="notice")

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

metadata.create_all(bind=engine)
