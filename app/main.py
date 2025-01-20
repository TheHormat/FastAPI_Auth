from fastapi import FastAPI
from app.api.routes.auth_routes import router as auth_router
from app.api.routes.google_auth_routes import router as google_auth_router
from app.db.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Include the routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(google_auth_router, prefix="/google", tags=["Google Authentication"])