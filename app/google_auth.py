from google.auth.transport.requests import Request
from google.oauth2 import id_token
from requests_oauthlib import OAuth2Session
import requests
from dotenv import load_dotenv
import os

load_dotenv()
# Load your Google Client ID and Secret
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_DISCOVERY_URL = os.getenv("GOOGLE_DISCOVERY_URL")
REDIRECT_URI = os.getenv("REDIRECT_URI")


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


def get_google_auth_url():
    provider_cfg = get_google_provider_cfg()
    authorization_endpoint = provider_cfg["authorization_endpoint"]
    oauth2_session = OAuth2Session(
        client_id=GOOGLE_CLIENT_ID,
        redirect_uri=REDIRECT_URI,
        scope=["openid", "email", "profile"],
    )
    auth_url, state = oauth2_session.authorization_url(authorization_endpoint)
    return auth_url, state


def fetch_google_user(token):
    id_info = id_token.verify_oauth2_token(token, Request(), GOOGLE_CLIENT_ID)
    return id_info
