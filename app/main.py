from fastapi import FastAPI, HTTPException, Depends, Request
import requests
from requests_oauthlib import OAuth2Session
from sqlalchemy.orm import Session
from app.models import User, Base
from app.schemas import UserRegisterSchema, UserLoginSchema
from app.database import SessionLocal, engine
from app.auth import create_access_token
from app.google_auth import (
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    REDIRECT_URI,
    get_google_auth_url,
    fetch_google_user,
    get_google_provider_cfg,
)
from app.crud import get_user_by_phone_number, create_user
from app.dependencies import (
    get_current_user,
)

Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/register")
def register_user(user: UserRegisterSchema, db: Session = Depends(get_db)):
    # Validate passwords match
    user.validate_passwords()

    # Check if phone number already exists
    existing_user = get_user_by_phone_number(db, user.phone_number)
    if existing_user:
        raise HTTPException(status_code=400, detail="Phone number already registered")

    # Create a new user instance
    new_user = User(
        username=user.username,
        phone_number=user.phone_number,
    )
    new_user.hash_password(user.password)  # Hash the password

    # Add and commit the user to the database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully"}


@app.post("/login")
def login_user(credentials: UserLoginSchema, db: Session = Depends(get_db)):
    user = get_user_by_phone_number(db, credentials.phone_number)
    if not user or not user.verify_password(credentials.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create a JWT token
    access_token = create_access_token(data={"sub": user.phone_number})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/protected")
def protected_route(current_user: dict = Depends(get_current_user)):
    """A route protected by JWT authentication."""
    return {"message": f"Welcome, {current_user['sub']}!"}


@app.get("/auth/google/login")
def google_login():
    """Redirect user to Google's OAuth 2.0 server."""
    auth_url, _ = get_google_auth_url()
    return {"auth_url": auth_url}


@app.get("/register/google/callback")
def google_callback(request: Request, db: Session = Depends(get_db)):
    """Handle the callback from Google OAuth."""
    code = request.query_params.get("code")
    state = request.query_params.get("state")

    if not code:
        raise HTTPException(status_code=400, detail="Missing 'code' parameter")

    try:
        # Fetch Google's OAuth configuration
        provider_cfg = get_google_provider_cfg()
        token_endpoint = provider_cfg["token_endpoint"]

        # Exchange the authorization code for an access token
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

        # Extract the ID token and fetch user info
        id_token = token_data.get("id_token")
        if not id_token:
            raise HTTPException(status_code=400, detail="ID token missing in response")

        user_info = fetch_google_user(id_token)
        email = user_info.get("email")
        name = user_info.get("name")

        # Check if user exists by email
        existing_user = db.query(User).filter(User.email == email).first()
        if not existing_user:
            # Create a new user
            user_data = {
                "username": name,
                "email": email,  # Set email explicitly
                "phone_number": None,  # No phone number for Google login
                "password_hash": None,  # No password for Google login
            }
            create_user(db, user_data)

        # Generate and return a JWT token
        access_token = create_access_token(data={"sub": email})
        return {"access_token": access_token, "token_type": "bearer"}

    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error during Google authentication: {str(e)}"
        )
