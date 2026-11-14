from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.auth import UserRegister, UserLogin, AuthResponse
from app.services.auth_service import register_user, login_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=AuthResponse)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    return await register_user(db, data)


@router.post("/login", response_model=AuthResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    return await login_user(db, data)


@router.get("/seed-demo")
@router.post("/seed-demo")
async def seed_demo_endpoint(db: AsyncSession = Depends(get_db)):
    try:
        from seed_demo_data import seed_session
        await seed_session(db, "Production Neon Database")
        return {"status": "success", "message": "Alex Morgan 6-week demo data successfully seeded"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
