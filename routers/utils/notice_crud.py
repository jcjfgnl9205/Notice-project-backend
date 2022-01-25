from sqlalchemy.orm import Session

from ..notices import schemas
from ..models import Notices

# List
def get_notices(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Notices).offset(skip).limit(limit).all()

# Detail
def get_notice(db: Session, notice_id: int):
    return db.query(Notices).filter(Notices.id == notice_id).first()

# Create
def create_notice(db: Session, notice: schemas.NoticeCreate, owner_id: int):
    db_notice = Notices(**notice.dict(), owner_id=owner_id)
    db.add(db_notice)
    db.commit()
    db.refresh(db_notice)
    return db_notice
