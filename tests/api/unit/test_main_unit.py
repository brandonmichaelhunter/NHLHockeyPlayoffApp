import httpx
import pytest
from httpx import ASGITransport, AsyncClient
from pytest_httpx import HTTPXMock, httpx_mock
from pytest_httpx import HTTPXMock
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
async def test_read_nhl_scores_with_valid_date(httpx_mock: HTTPXMock):
          # Mock the database response for a valid date
          mockNHLScores = [{"date": "2024-05-01", "home_team":  "A", "away_team": "B"}]

          # mock database session
          mockDBSession = MagicMock()

          # mock the session.exec().all() call.
          mockDBSession.exec.return_value.all.return_value = mockNHLScores

          # Override the get_session dependency to return our mock session.
          def override_get_session():
              yield mockDBSession

          # Overriding the Session dependency in the FastAPI app to use our mock session.
          main_module.app.dependency_overrides[main_module.get_session] = override_get_session

          try:
                # Use ASGITransport to connect the client directly to the FastAPI app
                async with AsyncClient(transport=ASGITransport(app=main_module.app), base_url="http://localhost") as ac:
                    response = await ac.get("/nhl_scores", params={"nhlScoreDateSelect": "2024-05-01"}, headers={"hx-request": "false"})

                # Assert the response
                assert response.status_code == 200, "Expected a 200 OK response for a valid date"
                assert response.json() == mockNHLScores, "Expected the mocked NHL scores to be returned in the response"
          finally:
                 main_module.app.dependency_overrides.clear()

@pytest.mark.unit
@pytest.mark.anyio
@pytest.mark.parametrize(
    "invalid_date, expected_payload",
    [
        ("2024-05-0", [])
    ],
)
async def test_read_nhl_scores_with_invalid_date(invalid_date, expected_payload):
          # Mock the database response for a valid date
          mockNHLScores = [{"date": "2024-05-01", "home_team":  "A", "away_team": "B"}]

          # mock database session
          mockDBSession = MagicMock()

          def exec_side_effect(stmt):
              params = stmt.compile().params
              selected_date = (
                    params.get("date_1") or
                    params.get("nhlScoreDateSelect_1") or
                    params.get("param_1"))

              result = MagicMock()
              result.all.return_value = mockNHLScores if selected_date == "2024-05-01" else []
              return result


          mockDBSession.exec.side_effect = exec_side_effect

          # Override the get_session dependency to return our mock session.
          def override_get_session():
              yield mockDBSession

          # Overriding the Session dependency in the FastAPI app to use our mock session.
          main_module.app.dependency_overrides[main_module.get_session] = override_get_session

          try:
                # Use ASGITransport to connect the client directly to the FastAPI app
                async with AsyncClient(transport=ASGITransport(app=main_module.app), base_url="http://localhost") as ac:
                    response = await ac.get("/nhl_scores", params={"nhlScoreDateSelect": invalid_date}, headers={"hx-request": "false"})

                # Assert the response
                assert response.status_code == 200, "Expected a 200 OK response for a valid date"
                assert response.json() == expected_payload, "Expected the mocked NHL scores not to be returned in the response"
          finally:
                 main_module.app.dependency_overrides.clear()


@pytest.mark.unit
@pytest.mark.anyio
async def test_nhl_stats_returns_stats_html_template():

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
                    "/stats",
                    params={},
                    headers={},
                )

        assert response.status_code == 200
        assert response.text == "rendered template"
        template_mock.assert_called_once()
        _, kwargs = template_mock.call_args
        assert kwargs["name"] == "stats.html"
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

@pytest.mark.unit
@pytest.mark.anyio
async def test_health_live():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost") as ac:
        response = await ac.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "alive"}

@pytest.mark.unit
@pytest.mark.anyio
async def test_health_ready_db_connection():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost") as ac:
        response = await ac.get("/health/ready")

    assert response.status_code == 200
    assert response.text == '"Database connection successful"'

@pytest.mark.unit
@pytest.mark.anyio
async def test_nhl_schedule_returns_schedule_html_template():

    # Mock the database session.
    mock_session = MagicMock()


    # Override the get_session dependency to return our mock session.
    def override_get_session():
        yield mock_session

    # Overriding the Session dependency in the FastAPI app to use our mock session.
    main_module.app.dependency_overrides[main_module.get_session] = override_get_session

    try:
        # Mock the templates.TemplateResponse object that returns a
        # HTMLResponse object with the content property  set to 'rendered template'.
        with patch.object(
            main_module.templates, # Represents the Jinja2Templates instance
            "TemplateResponse", # Represents an attribute on the object to swap out with a MagicMock
            return_value=HTMLResponse(content="rendered template"), # Represents what the mock returns whenenver templates.TemplateResponse is called.
        ) as template_mock:
            async with AsyncClient(transport=ASGITransport(app=main_module.app), base_url="http://localhost") as ac:
                response = await ac.get(
                    "/schedule",
                    params={},
                    headers={},
                )

        assert response.status_code == 200
        assert response.text == "rendered template"
        template_mock.assert_called_once()
        # verifies that the correct data is returned from the TemplateResponse call.
        _, kwargs = template_mock.call_args
        assert kwargs["name"] == "schedule.html"
        assert kwargs["context"] == {}
    finally:
        main_module.app.dependency_overrides.clear()
