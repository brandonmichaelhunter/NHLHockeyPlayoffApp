import pytest
from httpx import ASGITransport, AsyncClient
from src.api.hockeyplayoffapi.main import app
from unittest.mock import MagicMock, patch
from sqlmodel import Field, Session, SQLModel, create_engine, select
from fastapi import HTTPException
from src.api.hockeyplayoffapi.models.nhl_scores import nhl_scores
from src.api.hockeyplayoffapi import main as main_module
from fastapi.responses import HTMLResponse, JSONResponse

@pytest.mark.integration
@pytest.mark.anyio
async def test_health_live():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost") as ac:
        response = await ac.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "alive"}

@pytest.mark.integration
@pytest.mark.anyio
async def test_health_ready_db_connection():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost") as ac:
        response = await ac.get("/health/ready")

    assert response.status_code == 200
    assert response.text == '"Database connection successful"'

@pytest.mark.integration
@pytest.mark.anyio
async def test_read_nhl_scores_returns_html_with_hx_header_equal_false(tmp_path):
          # set db paht to test database.
          test_db_file = tmp_path / "test_nhl_db.db"
          # create a test engine use to create the test database.
          test_engine = create_engine(f"sqlite:///{test_db_file}")
          # set the app engine with a local one.
          main_module.engine = test_engine

          try:
              # create the test tables in our test database.
              SQLModel.metadata.create_all(test_engine)
              with Session(test_engine) as dbSession:
                   dbSession.add(nhl_scores(date="2024-05-01", home_team="Rangers", home_team_image="home.png", away_team="Bruins", away_team_image="away.png"))
                   dbSession.add(nhl_scores(date="2024-05-01", home_team="Leafs", home_team_image="home.png", away_team="Canadiens", away_team_image="away.png"))
                   dbSession.commit()

              # call the api.
              async with AsyncClient(transport=ASGITransport(app=main_module.app), base_url="http://localhost") as ac:
                   response = await ac.get("/nhl_scores", params={"nhlScoreDateSelect": "2024-05-01"}, headers={"hx-request": "false"})

              # assertons
              assert response.status_code == 200
              assert "application/json" in response.headers["content-type"]

          finally:
              main_module.engine = None

@pytest.mark.integration
@pytest.mark.anyio
async def test_read_nhl_scores_integration_returns_html_for_hx(tmp_path):
    db_file = tmp_path / "test_scores_hx.db" # set path to db file.
    test_engine = create_engine(f"sqlite:///{db_file}") # create sqlite engine with db path.
    original_engine = main_module.engine
    main_module.engine = test_engine #  set the app engine with a local one.

    try:
        SQLModel.metadata.create_all(test_engine) # create test tables in our test database.
        with Session(test_engine) as s: # add test data to the test database.
            s.add(
                nhl_scores(
                    date="2024-05-01",
                    home_team="Rangers",
                    home_team_image="home.png",
                    away_team="Bruins",
                    away_team_image="away.png",
                )
            )
            s.commit()

        async with AsyncClient(transport=ASGITransport(app=main_module.app),base_url="http://localhost") as ac:
            response = await ac.get(
                "/nhl_scores",
                params={"nhlScoreDateSelect": "2024-05-01"},
                headers={"hx-request": "true"},
            )

        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "Rangers" in response.text
        assert "Bruins" in response.text
    finally:
        main_module.engine = original_engine
