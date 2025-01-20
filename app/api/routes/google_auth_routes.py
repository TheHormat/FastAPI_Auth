from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from app.services.google_auth_service import get_google_auth_url, fetch_google_user, get_google_provider_cfg
from app.services.auth_service import create_access_token
from app.dependencies.auth_dependencies import get_db
from app.db.auth_models import User
from app.crud.auth_crud import create_user
from app.services.google_auth_service import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, REDIRECT_URI
import requests

router = APIRouter()

@router.get("/auth/google/login")
def google_login():
    auth_url, _ = get_google_auth_url()
    return {"auth_url": auth_url}


@router.get("/register/google/callback")
def google_callback(request: Request, db: Session = Depends(get_db)):
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Missing 'code' parameter")

    provider_cfg = get_google_provider_cfg()
    token_endpoint = provider_cfg["token_endpoint"]

    token_response = requests.post(
        token_endpoint,
        data={
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token_response.raise_for_status()
    token_data = token_response.json()

    id_token = token_data.get("id_token")
    if not id_token:
        raise HTTPException(status_code=400, detail="ID token missing in response")

    user_info = fetch_google_user(id_token)
    email = user_info.get("email")
    name = user_info.get("name")

    existing_user = db.query(User).filter(User.email == email).first()
    if not existing_user:
        user_data = {"username": name, "email": email, "phone_number": None, "password_hash": None}
        create_user(db, user_data)

    access_token = create_access_token(data={"sub": email})
    return {"access_token": access_token, "token_type": "bearer"}