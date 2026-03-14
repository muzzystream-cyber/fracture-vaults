from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.session import engine, Base
from app.api.endpoints import auth, users, paper, watchlists, performance

# Import all models so SQLAlchemy can create tables
from app.models import user, trading

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Premium Market Watchlist Scanner with Paper Trading & Observer Progression",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
app.include_router(paper.router, prefix=f"{settings.API_V1_STR}/paper", tags=["paper-trading"])
app.include_router(watchlists.router, prefix=f"{settings.API_V1_STR}/watchlists", tags=["watchlists"])
app.include_router(performance.router, prefix=f"{settings.API_V1_STR}/performance", tags=["performance"])

@app.get("/health")
def health():
    return {
        "status": "operational",
        "app": settings.PROJECT_NAME,
        "message": "The Fracture Vaults are open. The pattern is visible."
    }
