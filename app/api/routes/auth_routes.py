from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.schemas.auth_schemas import UserRegisterSchema, UserLoginSchema
from app.crud.auth_crud import get_user_by_phone_number
from app.dependencies.auth_dependencies import get_current_user, get_db
from app.auth import create_access_token
from app.db.auth_models import User

router = APIRouter()

@router.post("/register")
def register_user(user: UserRegisterSchema, db: Session = Depends(get_db)):
    user.validate_passwords()

    if get_user_by_phone_number(db, user.phone_number):
        raise HTTPException(status_code=400, detail="Phone number already registered")

    new_user = User(username=user.username, phone_number=user.phone_number)
    new_user.hash_password(user.password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully"}


@router.post("/login")
def login_user(credentials: UserLoginSchema, db: Session = Depends(get_db)):
    user = get_user_by_phone_number(db, credentials.phone_number)
    if not user or not user.verify_password(credentials.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.phone_number})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/protected")
def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": f"Welcome, {current_user['sub']}!"}