import pytest
from httpx import ASGITransport, AsyncClient
from src.api.hockeyplayoffapi.main import app
from unittest.mock import MagicMock, patch
from sqlmodel import Session
from fastapi import HTTPException
from src.api.hockeyplayoffapi.models.nhl_scores import nhl_scores
from src.api.hockeyplayoffapi import main as main_module
from fastapi.responses import HTMLResponse

@pytest.mark.unit
@pytest.mark.anyio
async def test_nhl_scores_returns_json_without_hx_header():

    fake_scores = [{"date": "2024-05-01", "home_team": "A", "away_team": "B"}]
    mock_session = MagicMock()
    mock_session.exec.return_value.all.return_value = fake_scores

    def override_get_session():
        yield mock_session

    main_module.app.dependency_overrides[main_module.get_session] = override_get_session

    try:
        async with AsyncClient(transport=ASGITransport(app=main_module.app), base_url="http://localhost") as ac:
            response = await ac.get("/nhl_scores", params={"nhlScoreDateSelect": "2024-05-01"}, headers={"hx-request": "false"})

        assert response.status_code == 200
        assert response.json() == fake_scores
        mock_session.exec.assert_called_once()
    finally:
        main_module.app.dependency_overrides.clear()

@pytest.mark.unit
@pytest.mark.anyio
async def test_nhl_scores_returns_template_with_hx_header():
    
    # Mock the nhl_scores fake data.
    fake_scores = [{"date": "2024-05-01", "home_team": "A", "away_team": "B"}]
    # Mock the database session.
    mock_session = MagicMock()
    # Set up the mock to return the fake scores when exec(). all() is called.
    mock_session.exec.return_value.all.return_value = fake_scores

    # Override the get_session dependency to return our mock session.
    def override_get_session():
        yield mock_session
        
    # Overriding the Session dependency in the FastAPI app to use our mock session.
    main_module.app.dependency_overrides[main_module.get_session] = override_get_session

    try:
        # 
        with patch.object(
            main_module.templates,
            "TemplateResponse",
            return_value=HTMLResponse(content="rendered template"),
        ) as template_mock:
            async with AsyncClient(transport=ASGITransport(app=main_module.app), base_url="http://localhost") as ac:
                response = await ac.get(
                    "/nhl_scores",
                    params={"nhlScoreDateSelect": "2024-05-01"},
                    headers={"hx-request": "true"},
                )

        assert response.status_code == 200
        assert response.text == "rendered template"
        template_mock.assert_called_once()
        _, kwargs = template_mock.call_args
        assert kwargs["name"] == "nhlscores.html"
        assert kwargs["context"]["nhlScores"] == fake_scores
    finally:
        main_module.app.dependency_overrides.clear()


            
@pytest.mark.unit
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
