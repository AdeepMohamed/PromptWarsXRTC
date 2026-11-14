from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import init_db
from app.api.routes.auth import router as auth_router
from app.api.routes.learner import router as learner_router
from app.api.routes.career import router as career_router
from app.api.routes.skills import router as skills_router
from app.api.routes.roadmap import router as roadmap_router
from app.api.routes.assessment import router as assessment_router
from app.api.routes.mentor import router as mentor_router
from app.api.routes.agents import router as agents_router
from app.api.routes.analytics import router as analytics_router
from app.api.routes.project import router as project_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables on startup
    try:
        await init_db()
    except Exception as e:
        print(f"Warning: database initialization failed (will retry per request): {e}")
    yield


app = FastAPI(
    title="COGNIFY AI — Career Intelligence Platform",
    description="Multi-agent career intelligence, skill gap analysis, and adaptive learning roadmap platform.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes under both /api and root for maximum client URL resilience
routers = [
    auth_router,
    learner_router,
    career_router,
    skills_router,
    roadmap_router,
    assessment_router,
    mentor_router,
    agents_router,
    analytics_router,
    project_router,
]
for r in routers:
    app.include_router(r, prefix="/api")
    app.include_router(r)


@app.get("/")
async def root():
    return {
        "app": "COGNIFY AI",
        "tagline": "Transform Knowledge into Career Intelligence",
        "version": "1.0.0",
        "status": "operational",
    }


@app.get("/health")
@app.get("/api/health")
async def health():
    return {"status": "healthy"}
