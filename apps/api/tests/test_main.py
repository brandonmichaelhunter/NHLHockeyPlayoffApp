import pytest
from httpx import ASGITransport, AsyncClient
from apps.api.hockeyplayoffapi.main import app

@pytest.mark.anyio
async def test_root():
    # Use ASGITransport to connect the client directly to the FastAPI app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost") as ac:
        response = await ac.get("/appname")
    
    assert response.status_code == 200
    assert response.json() == {"app_name": "Hockey Playoff API"}

@pytest.mark.anyio
async def test_health_live():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost") as ac:
        response = await ac.get("/health/live")
        
    assert response.status_code == 200
    assert response.json() == {"status": "alive"}

@pytest.mark.anyio
async def test_health_ready_db_connection():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost") as ac:
        response = await ac.get("/health/ready")

    assert response.status_code == 200
    assert response.text == '"Database connection successful"'