import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.security import verify_password, hash_password, create_access_token


@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


@pytest.mark.asyncio
async def test_root_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["app"] == "COGNIFY AI"
        assert data["status"] == "operational"


def test_password_hashing():
    password = "secret_password_123"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong_password", hashed) is False


def test_jwt_token_generation():
    token = create_access_token(data={"sub": "test-uuid-1234", "role": "learner"})
    assert isinstance(token, str)
    assert len(token) > 20
