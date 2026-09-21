import pytest
from httpx import ASGITransport, AsyncClient
from unittest.mock import MagicMock, patch

from fastapi.responses import HTMLResponse
from src.api.hockeyplayoffapi import main as main_module


@pytest.mark.api_unit
@pytest.mark.anyio
async def test_nhl_scores_returns_json_without_hx_header():
    fake_scores = [{"date": "2024-05-01", "home_team": "A", "away_team": "B"}]

    # mocks the get_nhl_scores_by_date function to return fake_scores
    with patch.object(
        main_module,
        "get_nhl_scores_by_date",
        return_value=fake_scores,
    ) as mock_get_scores:
        # creates an asynchronous HTTP client to send requests to the FastAPI application
        async with AsyncClient(
            transport=ASGITransport(app=main_module.app),
            base_url="http://localhost",
        ) as ac:
            # sends a GET request to the /nhl_scores endpoint with the specified query parameter and header
            response = await ac.get(
                "/nhl_scores",
                params={"nhlScoreDateSelect": "2024-05-01"},
                headers={"hx-request": "false"},
            )

    assert response.status_code == 200
    assert response.json() == fake_scores
    mock_get_scores.assert_called_once_with(nhlScoreDateSelect="2024-05-01")


@pytest.mark.api_unit
@pytest.mark.anyio
async def test_nhl_scores_returns_template_with_hx_header():
    fake_scores = [{"date": "2024-05-01", "home_team": "A", "away_team": "B"}]

    with (
        patch.object(
            main_module,
            "get_nhl_scores_by_date",
            return_value=fake_scores,
        ) as mock_get_scores,
        patch.object(
            main_module.templates,
            "TemplateResponse",
            return_value=HTMLResponse(content="rendered template"),
        ) as template_mock,
    ):
        async with AsyncClient(
            transport=ASGITransport(app=main_module.app),
            base_url="http://localhost",
        ) as ac:
            response = await ac.get(
                "/nhl_scores",
                params={"nhlScoreDateSelect": "2024-05-01"},
                headers={"hx-request": "true"},
            )

    assert response.status_code == 200
    assert response.text == "rendered template"
    mock_get_scores.assert_called_once_with(nhlScoreDateSelect="2024-05-01")
    template_mock.assert_called_once()
    _, kwargs = template_mock.call_args
    assert kwargs["name"] == "nhlscores.html"
    assert kwargs["context"]["nhlScores"] == fake_scores


@pytest.mark.api_unit
@pytest.mark.anyio
async def test_root_and_health_routes():
    async with AsyncClient(
        transport=ASGITransport(app=main_module.app),
        base_url="http://localhost",
    ) as ac:
        app_response = await ac.get("/appname")
        health_response = await ac.get("/health")
        live_response = await ac.get("/health/live")

    assert app_response.status_code == 200
    assert app_response.json() == {"app_name": "Hockey Playoff API"}
    assert health_response.status_code == 200
    assert health_response.json() == {"status": "alive"}
    assert live_response.status_code == 200
    assert live_response.json() == {"status": "alive"}


@pytest.mark.api_unit
@pytest.mark.anyio
async def test_index_template_renders():
    with patch.object(
        main_module.templates,
        "TemplateResponse",
        return_value=HTMLResponse(content="rendered template"),
    ) as template_mock:
        async with AsyncClient(
            transport=ASGITransport(app=main_module.app),
            base_url="http://localhost",
        ) as ac:
            response = await ac.get("/")

    assert response.status_code == 200
    assert response.text == "rendered template"
    template_mock.assert_called_once()
    _, kwargs = template_mock.call_args
    assert kwargs["name"] == "index.html"


@pytest.mark.api_unit
@pytest.mark.anyio
async def test_stats_template_renders():
    with patch.object(
        main_module.templates,
        "TemplateResponse",
        return_value=HTMLResponse(content="rendered template"),
    ) as template_mock:
        async with AsyncClient(
            transport=ASGITransport(app=main_module.app),
            base_url="http://localhost",
        ) as ac:
            response = await ac.get("/stats")

    assert response.status_code == 200
    assert response.text == "rendered template"
    template_mock.assert_called_once()
    _, kwargs = template_mock.call_args
    assert kwargs["name"] == "stats.html"


@pytest.mark.api_unit
@pytest.mark.anyio
async def test_schedule_template_renders():
    with patch.object(
        main_module.templates,
        "TemplateResponse",
        return_value=HTMLResponse(content="rendered template"),
    ) as template_mock:
        async with AsyncClient(
            transport=ASGITransport(app=main_module.app),
            base_url="http://localhost",
        ) as ac:
            response = await ac.get("/schedule")

    assert response.status_code == 200
    assert response.text == "rendered template"
    template_mock.assert_called_once()
    _, kwargs = template_mock.call_args
    assert kwargs["name"] == "schedule.html"
    assert kwargs["context"] == {}


@pytest.mark.api_unit
@pytest.mark.anyio
async def test_get_playoff_game_dates_returns_json():
    fake_game_dates = [{"date": "2026-06-06"}, {"date": "2026-06-05"}]
    original_db_manager = main_module.db_manager
    mock_db = MagicMock()
    mock_db.get_playoff_game_dates.return_value = fake_game_dates
    main_module.db_manager = mock_db

    try:
        async with AsyncClient(
            transport=ASGITransport(app=main_module.app),
            base_url="http://localhost",
        ) as ac:
            response = await ac.get("/get_playoff_game_dates")
    finally:
        main_module.db_manager = original_db_manager

    assert response.status_code == 200
    assert response.json() == fake_game_dates
    mock_db.get_playoff_game_dates.assert_called_once_with()


@pytest.mark.api_unit
@pytest.mark.anyio
@patch("src.api.hockeyplayoffapi.main.get_nhl_playoff_schedule_games")
async def test_get_nhl_schedule_returns_valid_nhl_schedule(
    mock_get_nhl_playoff_schedule_games,
):
    fake_nhl_schedule = [
        {
            "gameDate": "2026-06-06",
            "seriesTitle": "Stanley Cup Final",
        }
    ]
    mock_get_nhl_playoff_schedule_games.return_value = fake_nhl_schedule

    with patch.object(
        main_module.templates,
        "TemplateResponse",
        return_value=HTMLResponse(content="rendered template"),
    ) as template_mock:
        async with AsyncClient(
            transport=ASGITransport(app=main_module.app),
            base_url="http://localhost",
        ) as ac:
            response = await ac.get("/get_nhl_schedule")

    assert response.status_code == 200
    assert response.text == "rendered template"
    mock_get_nhl_playoff_schedule_games.assert_called_once_with()
    template_mock.assert_called_once()
    _, kwargs = template_mock.call_args
    assert kwargs["name"] == "nhl_schedule.html"
    assert kwargs["context"]["schedules"] == fake_nhl_schedule


@pytest.mark.api_unit
@pytest.mark.anyio
@patch("src.api.hockeyplayoffapi.main.get_nhl_teams_data")
async def test_get_nhl_teams_returns_valid_nhl_teams(mock_get_nhl_teams_data):
    fake_nhl_teams = [{"id": 30, "team_name": "Carolina Hurricanes"}]
    mock_get_nhl_teams_data.return_value = fake_nhl_teams

    with patch.object(
        main_module.templates,
        "TemplateResponse",
        return_value=HTMLResponse(content="rendered template"),
    ) as template_mock:
        async with AsyncClient(
            transport=ASGITransport(app=main_module.app),
            base_url="http://localhost",
        ) as ac:
            response = await ac.get("/get_nhl_teams")

    assert response.status_code == 200
    assert response.text == "rendered template"
    mock_get_nhl_teams_data.assert_called_once_with()
    template_mock.assert_called_once()
    _, kwargs = template_mock.call_args
    assert kwargs["name"] == "nhl_teams_options.html"
    assert kwargs["context"]["teams"] == fake_nhl_teams


@pytest.mark.api_unit
@pytest.mark.anyio
@patch("src.api.hockeyplayoffapi.main.get_nhl_goal_leaders")
@patch("src.api.hockeyplayoffapi.main.get_nhl_plusminus_leaders")
@patch("src.api.hockeyplayoffapi.main.get_nhl_points_leaders")
@patch("src.api.hockeyplayoffapi.main.get_nhl_goaltending_save_percentage_leaders")
@patch("src.api.hockeyplayoffapi.main.get_nhl_goaltending_gaa_leaders")
@patch("src.api.hockeyplayoffapi.main.get_nhl_goaltending_wins_leaders")
async def test_get_nhl_stats_returns_stats_leaders_template(
    mock_get_nhl_goaltending_wins_leaders,
    mock_get_nhl_goaltending_gaa_leaders,
    mock_get_nhl_goaltending_save_percentage_leaders,
    mock_get_nhl_points_leaders,
    mock_get_nhl_plusminus_leaders,
    mock_get_nhl_goal_leaders,
):
    fake_goal_ranks = [{"player_id": 1, "total_goals": 5}]
    fake_plusminus_ranks = [{"player_id": 2, "plus_minus": 4}]
    fake_points_ranks = [{"player_id": 3, "total_points": 8}]
    fake_save_pct_ranks = [{"player_id": 4, "save_percentage": 0.945}]
    fake_gaa_ranks = [{"player_id": 5, "gaa": 1.85}]
    fake_wins_ranks = [{"player_id": 6, "wins": 3}]

    mock_get_nhl_goal_leaders.return_value = fake_goal_ranks
    mock_get_nhl_plusminus_leaders.return_value = fake_plusminus_ranks
    mock_get_nhl_points_leaders.return_value = fake_points_ranks
    mock_get_nhl_goaltending_save_percentage_leaders.return_value = fake_save_pct_ranks
    mock_get_nhl_goaltending_gaa_leaders.return_value = fake_gaa_ranks
    mock_get_nhl_goaltending_wins_leaders.return_value = fake_wins_ranks

    with patch.object(
        main_module.templates,
        "TemplateResponse",
        return_value=HTMLResponse(content="rendered template"),
    ) as template_mock:
        async with AsyncClient(
            transport=ASGITransport(app=main_module.app),
            base_url="http://localhost",
        ) as ac:
            response = await ac.get("/get_nhl_stats", params={"teams": 7})

    assert response.status_code == 200
    assert response.text == "rendered template"
    mock_get_nhl_goal_leaders.assert_called_once_with(TeamName=7)
    mock_get_nhl_plusminus_leaders.assert_called_once_with(TeamName=7)
    mock_get_nhl_points_leaders.assert_called_once_with(TeamName=7)
    mock_get_nhl_goaltending_save_percentage_leaders.assert_called_once_with(TeamName=7)
    mock_get_nhl_goaltending_gaa_leaders.assert_called_once_with(TeamName=7)
    mock_get_nhl_goaltending_wins_leaders.assert_called_once_with(TeamName=7)
    template_mock.assert_called_once()
    _, kwargs = template_mock.call_args
    assert kwargs["name"] == "nhlstats_leaders.html"
    assert kwargs["context"]["playerGoalRanks"] == fake_goal_ranks
    assert kwargs["context"]["playerPlusMinusRanks"] == fake_plusminus_ranks
    assert kwargs["context"]["playerPointsRanks"] == fake_points_ranks
    assert kwargs["context"]["goalieSavePercentageRanks"] == fake_save_pct_ranks
    assert kwargs["context"]["goalieGAARanks"] == fake_gaa_ranks
    assert kwargs["context"]["goalieWinsRanks"] == fake_wins_ranks


@pytest.mark.api_unit
@pytest.mark.parametrize(
    "func, kwargs",
    [
        (main_module.get_nhl_teams_data, {}),
        (main_module.get_nhl_goal_leaders, {"TeamName": 7}),
        (main_module.get_nhl_plusminus_leaders, {"TeamName": 7}),
        (main_module.get_nhl_points_leaders, {"TeamName": 7}),
        (main_module.get_nhl_goaltending_save_percentage_leaders, {"TeamName": 7}),
        (main_module.get_nhl_goaltending_gaa_leaders, {"TeamName": 7}),
        (main_module.get_nhl_goaltending_wins_leaders, {"TeamName": 7}),
        (main_module.get_nhl_playoff_schedule_games, {}),
    ],
)
def test_main_helper_functions_raise_when_db_not_initialized(func, kwargs):
    original_db_manager = main_module.db_manager
    main_module.db_manager = None

    try:
        with pytest.raises(ValueError, match="DB manager has not been initialized."):
            func(**kwargs)
    finally:
        main_module.db_manager = original_db_manager
