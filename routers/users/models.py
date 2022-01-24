from sqlalchemy import Boolean, Column, Integer, String
from db.session import Base, metadata, engine

#User Table
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


metadata.create_all(bind=engine)
