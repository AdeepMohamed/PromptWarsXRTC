from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.project import ProjectSubmitRequest
from app.services.project_service import submit_project, list_projects

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("/submit")
async def create_project(
    data: ProjectSubmitRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    project = await submit_project(db, user, data)
    return {"project": project}


@router.get("")
async def get_projects(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    projects = await list_projects(db, user)
    return {"projects": projects}
