from pydantic import BaseModel

class UserBase(BaseModel):
    username: str
    is_active: bool

#INSERT用のrequest Model
class UserCreate(BaseModel):
    email: str
    username: str
    first_name: str
    last_name: str
    password: str
    is_active: bool

#SELECT用のrequest Model
class UserSelect(BaseModel):
    id: int
    email: str
    username: str
    first_name: str
    last_name: str
    is_active: bool
    is_staff: bool

    class Config:
        orm_mode = True

#LOGIN用
class UserLogin(BaseModel):
    username: str
    password: str

#Token
class Token(BaseModel):
    access_token: str
    refresh_token: str
