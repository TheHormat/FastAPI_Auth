from sqlalchemy.orm import Session
from app.models import User

def get_user_by_phone_number(db: Session, phone_number: str):
    return db.query(User).filter(User.phone_number == phone_number).first()

def create_user(db: Session, user_data: dict):
    # Remove any unexpected keys like 'password'
    user_data.pop("password", None)
    new_user = User(**user_data)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user