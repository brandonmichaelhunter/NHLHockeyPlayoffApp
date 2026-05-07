import pytest
from httpx import ASGITransport, AsyncClient
from apps.api.hockeyplayoffapi.main import app
from unittest.mock import MagicMock, patch
from sqlmodel import Session
from fastapi import HTTPException
from apps.api.hockeyplayoffapi.models.nhl_scores import nhl_scores
from apps.api.hockeyplayoffapi import main as main_module
from fastapi.responses import HTMLResponse

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