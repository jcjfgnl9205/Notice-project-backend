from pydantic import BaseModel

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
    email: str
    username: str
    first_name: str
    last_name: str
    is_active: bool
