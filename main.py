from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.session import engine, Base
from app.api.endpoints import auth, users, paper, watchlists, performance, rewards
from app.models import user, trading

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="FII Observer Progression — Paper Trading, Rewards & Rank System",
    version="2.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,        prefix=f"{settings.API_V1_STR}/auth",        tags=["auth"])
app.include_router(users.router,       prefix=f"{settings.API_V1_STR}/users",       tags=["users"])
app.include_router(paper.router,       prefix=f"{settings.API_V1_STR}/paper",       tags=["paper-trading"])
app.include_router(watchlists.router,  prefix=f"{settings.API_V1_STR}/watchlists",  tags=["watchlists"])
app.include_router(performance.router, prefix=f"{settings.API_V1_STR}/performance", tags=["performance"])
app.include_router(rewards.router,     prefix=f"{settings.API_V1_STR}/rewards",     tags=["rewards"])

@app.get("/health")
def health():
    return {"status": "operational", "version": "2.0.0", "app": settings.PROJECT_NAME, "message": "The Fracture Vaults are open. The pattern is visible."}
