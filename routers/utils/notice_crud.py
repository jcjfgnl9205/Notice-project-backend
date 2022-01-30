from sqlalchemy.orm import Session

from ..notices import schemas
from ..models import Notices, Users
from datetime import datetime

# Listd
def get_notices(db: Session):
    return db.query(Notices).order_by(Notices.id.desc()).all()

# Detail
def get_notice(db: Session, notice_id: int):
    return db.query(Notices.title,
                    Notices.content,
                    Notices.views,
                    Notices.created_at,
                    Notices.updated_at,
                    Users.username,
                    Users.is_active)\
            .join(Users, Notices.owner_id == Users.id)\
            .filter(Notices.owner_id == Users.id)\
            .filter(Notices.id == notice_id)\
            .first()

# Create
def create_notice(db: Session, notice: schemas.NoticeCreate, owner_id: int):
    db_notice = Notices(**notice.dict(), owner_id=owner_id)
    db.add(db_notice)
    db.commit()
    db.refresh(db_notice) 
    return db_notice

# Delete
def delete_notice(db: Session, notice_id: str):
    db.query(Notices).filter(Notices.id == notice_id).delete()
    db.commit()
    return {"status" : 200, "transaction": "Successful" }

# Update
def update_notice(db: Session, notice_id: int, owner_id: int, notice: schemas.NoticeUpdate):
    db_notice = db.query(Notices).filter(Notices.id == notice_id)\
                                 .filter(Notices.owner_id == owner_id)\
                                 .first()

    db_notice.title = notice.title
    db_notice.content = notice.content
    db_notice.updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    db.add(db_notice)
    db.commit()

    return db_notice
