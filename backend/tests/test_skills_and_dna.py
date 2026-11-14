import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_list_skills_public():
    """Verify skills catalog endpoint returns valid skills with categories."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/skills")
        assert response.status_code == 200
        data = response.json()
        assert "skills" in data
        assert isinstance(data["skills"], list)


@pytest.mark.asyncio
async def test_careers_list():
    """Verify career roles catalog endpoint returns valid career paths."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/careers")
        assert response.status_code == 200
        data = response.json()
        assert "careers" in data
        assert isinstance(data["careers"], list)
