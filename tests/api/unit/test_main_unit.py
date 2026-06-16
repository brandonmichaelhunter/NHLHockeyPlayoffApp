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
# Confirm the correct html templates are return test methods.

@pytest.mark.unit
@pytest.mark.anyio
async def test_nhl_games_returns_index_html_template():

    # Override the get_session dependency to return a mock session.
    def override_get_session():
        yield MagicMock()

    # Overriding the Session dependecy in the FastAPI app to use our mock session.
    main_module.app.dependency_overrides[main_module.get_session] = override_get_session

    try:
        # mocks the return response
        with patch.object(
            main_module.templates, # Represents the Jinja2Templates instance
            "TemplateResponse", # Represents an attribute on the object to swap out with a MagicMock
            return_value=HTMLResponse(content="rendered template"), # Represents what the mock returns whenenver templates.TemplateResponse is called.
        ) as template_mock:
            async with AsyncClient(transport=ASGITransport(app=main_module.app), base_url="http://localhost") as ac:
                response = await ac.get(
                    "/",
                    params={},
                    headers={},
                )

        assert response.status_code == 200
        assert response.text == "rendered template"
        template_mock.assert_called_once()
        _, kwargs = template_mock.call_args
        assert kwargs["name"] == "index.html"
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

# ------------------------------------------------
# -- Confirm NHL Schedule endpoints return correct data.
# ------------------------------------------------
@pytest.mark.unit
@pytest.mark.anyio
@patch("src.api.hockeyplayoffapi.main.get_nhl_playoff_schedule_games")
async def test_get_nhl_schedule_returns_valid_nhl_schedule(mock_get_nhl_playoff_schedule_games):

    # Mock the nhl_scores fake data.
    fake_nhl_schedule = [
        {'gameDate': '2026-06-06', 'gameStartTime': '2026-06-07T00:00:00Z',
         'awayTeamName': 'Carolina Hurricanes', 'awayScore': 4, 'awayTeamNameAbbrv': 'CAR', 'awayTeamLogoUrl': 'https://assets.nhle.com/logos/nhl/svg/CAR_light.svg',
         'homeTeamName': 'Vegas Golden Knights', 'homeScore': 5, 'homeTeamNameAbbrv': 'VGK', 'homeTeamLogoUrl': 'https://assets.nhle.com/logos/nhl/svg/VGK_light.svg',
         'seriesTitle': 'Stanley Cup Final', 'playoffRound': '4', 'tvStation': 'ABC', 'homeTeamVenueName': 'T-Mobile Arena', 'winningGoaliePlayerID': 8479394,
         'goalieFirstName': 'Carter', 'goalieLastName': 'Hart', 'goalieHeadShotUrl': 'https://assets.nhle.com/mugs/nhl/20252026/VGK/8479394.png',
         'winningGoalScorerPlayerID': 8477447, 'skaterFirstName': 'Shea', 'skaterLastName': 'Theodore',
         'skaterHeadShotUrl': 'https://assets.nhle.com/mugs/nhl/20252026/VGK/8477447.png', 'seriesInfo': 'VGK leads series 2-1'}]

    mock_get_nhl_playoff_schedule_games.return_value = fake_nhl_schedule

    # Mock the database session.
    mock_session = MagicMock()

    # Override the get_session dependency to return our mock session.
    def override_get_session():
        yield mock_session

    # Overriding the Session dependency in the FastAPI app to use our mock session.
    main_module.app.dependency_overrides[main_module.get_session] = override_get_session

    try:
        with patch.object(
            main_module.templates,
            "TemplateResponse",
            return_value=HTMLResponse(content="rendered template"),
        ) as template_mock:
            async with AsyncClient(transport=ASGITransport(app=main_module.app), base_url="http://localhost") as ac:
                response = await ac.get("/get_nhl_schedule")

        assert response.status_code == 200
        assert response.text == "rendered template"

        mock_get_nhl_playoff_schedule_games.assert_called_once_with(session=mock_session)

        template_mock.assert_called_once()
        _, kwargs = template_mock.call_args
        assert kwargs["name"] == "nhl_schedule.html"
        assert kwargs["context"]["schedules"] == fake_nhl_schedule

    finally:
        main_module.app.dependency_overrides.clear()

@pytest.mark.unit
@pytest.mark.anyio
@patch("src.api.hockeyplayoffapi.main.get_nhl_teams")
async def test_get_nhl_teams_returns_valid_nhl_teams(mock_function):

    # Mock the nhl_scores fake data.
    fake_nhl_teams = [{"id":30, "team_name": "Carolina Hurricanes"}, {"id":54, "team_name": "Vegas Golden Knights"}]

    mock_function.return_value = fake_nhl_teams

    # Mock the database session.
    mock_session = MagicMock()

    # Override the get_session dependency to return our mock session.
    def override_get_session():
        yield mock_session

    # Overriding the Session dependency in the FastAPI app to use our mock session.
    main_module.app.dependency_overrides[main_module.get_session] = override_get_session

    try:
        with patch.object(
            main_module.templates,
            "TemplateResponse",
            return_value=HTMLResponse(content="rendered template"),
        ) as template_mock:
            async with AsyncClient(transport=ASGITransport(app=main_module.app), base_url="http://localhost") as ac:
                response = await ac.get("/get_nhl_teams")

        assert response.status_code == 200
        assert response.text == "rendered template"

        mock_function.assert_called_once_with(session=mock_session)

        template_mock.assert_called_once()
        _, kwargs = template_mock.call_args
        assert kwargs["name"] == "nhl_teams_options.html", "Expected the nhl_teams_options.html template to be rendered"
        assert kwargs["context"]["teams"] == fake_nhl_teams, "Expected the mocked NHL teams to be passed in the context of the template response"

    finally:
        main_module.app.dependency_overrides.clear()

@pytest.mark.unit
@pytest.mark.anyio
@patch("src.api.hockeyplayoffapi.main.get_nhl_goaltending_wins_leaders")
@patch("src.api.hockeyplayoffapi.main.get_nhl_goaltending_gaa_leaders")
@patch("src.api.hockeyplayoffapi.main.get_nhl_goaltending_save_percentage_leaders")
@patch("src.api.hockeyplayoffapi.main.get_nhl_points_leaders")
@patch("src.api.hockeyplayoffapi.main.get_nhl_plusminus_leaders")
@patch("src.api.hockeyplayoffapi.main.get_nhl_goal_leaders")
async def test_get_nhl_stats_returns_stats_leaders_template(
    mock_get_nhl_goal_leaders,
    mock_get_nhl_plusminus_leaders,
    mock_get_nhl_points_leaders,
    mock_get_nhl_goaltending_save_percentage_leaders,
    mock_get_nhl_goaltending_gaa_leaders,
    mock_get_nhl_goaltending_wins_leaders,
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

    mock_session = MagicMock()

    def override_get_session():
        yield mock_session

    main_module.app.dependency_overrides[main_module.get_session] = override_get_session

    try:
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

        mock_get_nhl_goal_leaders.assert_called_once_with(session=mock_session, TeamName=7)
        mock_get_nhl_plusminus_leaders.assert_called_once_with(session=mock_session, TeamName=7)
        mock_get_nhl_points_leaders.assert_called_once_with(session=mock_session, TeamName=7)
        mock_get_nhl_goaltending_save_percentage_leaders.assert_called_once_with(
            session=mock_session, TeamName=7
        )
        mock_get_nhl_goaltending_gaa_leaders.assert_called_once_with(
            session=mock_session, TeamName=7
        )
        mock_get_nhl_goaltending_wins_leaders.assert_called_once_with(
            session=mock_session, TeamName=7
        )

        template_mock.assert_called_once()
        _, kwargs = template_mock.call_args
        assert kwargs["name"] == "nhlstats_leaders.html"
        assert kwargs["context"]["playerGoalRanks"] == fake_goal_ranks
        assert kwargs["context"]["playerPlusMinusRanks"] == fake_plusminus_ranks
        assert kwargs["context"]["playerPointsRanks"] == fake_points_ranks
        assert kwargs["context"]["goalieSavePercentageRanks"] == fake_save_pct_ranks
        assert kwargs["context"]["goalieGAARanks"] == fake_gaa_ranks
        assert kwargs["context"]["goalieWinsRanks"] == fake_wins_ranks
    finally:
        main_module.app.dependency_overrides.clear()

@pytest.mark.unit
@pytest.mark.anyio
async def test_get_playoff_game_dates_returns_json():
    fake_game_dates = [
        {"date": "2026-06-06"},
        {"date": "2026-06-05"},
    ]

    mock_session = MagicMock()
    mock_session.execute.return_value.mappings.return_value.all.return_value = fake_game_dates

    def override_get_session():
        yield mock_session

    main_module.app.dependency_overrides[main_module.get_session] = override_get_session

    try:
        async with AsyncClient(
            transport=ASGITransport(app=main_module.app),
            base_url="http://localhost",
        ) as ac:
            response = await ac.get("/get_playoff_game_dates")

        assert response.status_code == 200
        assert response.json() == fake_game_dates
        mock_session.execute.assert_called_once()
    finally:
        main_module.app.dependency_overrides.clear()

def _result_with_rows(rows):
    result = MagicMock()
    result.mappings.return_value.all.return_value = rows
    return result


def _goal_row():
    return {
        "player_id": 1,
        "total_goals": 6,
        "league_ranking": 1,
        "player_firstname": "Connor",
        "player_lastname": "McDavid",
        "player_headshot": "https://example.com/mcdavid.png",
        "player_position": "C",
        "team_name": "Edmonton Oilers",
        "team_abbrv": "EDM",
        "team_logo": "https://example.com/edm.svg",
    }


def _plusminus_row():
    return {
        "player_id": 2,
        "plus_minus": 5,
        "league_ranking": 1,
        "player_firstname": "Aleksander",
        "player_lastname": "Barkov",
        "player_headshot": "https://example.com/barkov.png",
        "player_position": "C",
        "team_name": "Florida Panthers",
        "team_abbrv": "FLA",
        "team_logo": "https://example.com/fla.svg",
    }


def _points_row():
    return {
        "player_id": 3,
        "total_points": 11,
        "league_ranking": 1,
        "player_firstname": "Leon",
        "player_lastname": "Draisaitl",
        "player_headshot": "https://example.com/draisaitl.png",
        "player_position": "C",
        "team_name": "Edmonton Oilers",
        "team_abbrv": "EDM",
        "team_logo": "https://example.com/edm.svg",
    }


def _save_pct_row():
    return {
        "player_id": 4,
        "save_percentage": 0.945,
        "league_ranking": 1,
        "player_firstname": "Sergei",
        "player_lastname": "Bobrovsky",
        "player_headshot": "https://example.com/bobrovsky.png",
        "player_position": "G",
        "team_name": "Florida Panthers",
        "team_abbrv": "FLA",
        "team_logo": "https://example.com/fla.svg",
    }


def _gaa_row():
    return {
        "player_id": 5,
        "gaa": 1.84,
        "league_ranking": 1,
        "player_firstname": "Igor",
        "player_lastname": "Shesterkin",
        "player_headshot": "https://example.com/shesterkin.png",
        "player_position": "G",
        "team_name": "New York Rangers",
        "team_abbrv": "NYR",
        "team_logo": "https://example.com/nyr.svg",
    }


def _wins_row():
    return {
        "player_id": 6,
        "wins": 4,
        "league_ranking": 1,
        "player_firstname": "Stuart",
        "player_lastname": "Skinner",
        "player_headshot": "https://example.com/skinner.png",
        "player_position": "G",
        "team_name": "Edmonton Oilers",
        "team_abbrv": "EDM",
        "team_logo": "https://example.com/edm.svg",
    }


def _schedule_row():
    return {
        "gameDate": "2026-06-06",
        "gameStartTime": "2026-06-07T00:00:00Z",
        "awayTeamName": "Carolina Hurricanes",
        "awayScore": 4,
        "awayTeamNameAbbrv": "CAR",
        "awayTeamLogoUrl": "https://example.com/car.svg",
        "homeTeamName": "Vegas Golden Knights",
        "homeScore": 5,
        "homeTeamNameAbbrv": "VGK",
        "homeTeamLogoUrl": "https://example.com/vgk.svg",
        "seriesTitle": "Stanley Cup Final",
        "playoffRound": "4",
        "tvStation": "ABC",
        "homeTeamVenueName": "T-Mobile Arena",
        "winningGoaliePlayerID": 8479394,
        "goalieFirstName": "Carter",
        "goalieLastName": "Hart",
        "goalieHeadShotUrl": "https://example.com/goalie.png",
        "winningGoalScorerPlayerID": 8477447,
        "skaterFirstName": "Shea",
        "skaterLastName": "Theodore",
        "skaterHeadShotUrl": "https://example.com/skater.png",
        "seriesInfo": "VGK leads series 2-1",
    }


@pytest.mark.unit
@pytest.mark.parametrize(
    "func, kwargs, rows, expected_attr, expected_value, expected_params",
    [
        (
            main_module.get_nhl_teams,
            {},
            [{"id": 1, "team_name": "Boston Bruins"}],
            "team_name",
            "Boston Bruins",
            None,
        ),
        (
            main_module.get_nhl_goal_leaders,
            {"TeamName": 7},
            [_goal_row()],
            "total_goals",
            6,
            {"TeamName": 7},
        ),
        (
            main_module.get_nhl_plusminus_leaders,
            {"TeamName": 7},
            [_plusminus_row()],
            "plus_minus",
            5,
            {"TeamName": 7},
        ),
        (
            main_module.get_nhl_points_leaders,
            {"TeamName": 7},
            [_points_row()],
            "total_points",
            11,
            {"TeamName": 7},
        ),
        (
            main_module.get_nhl_goaltending_save_percentage_leaders,
            {"TeamName": 7},
            [_save_pct_row()],
            "save_percentage",
            0.945,
            {"TeamName": 7},
        ),
        (
            main_module.get_nhl_goaltending_gaa_leaders,
            {"TeamName": 7},
            [_gaa_row()],
            "gaa",
            1.84,
            {"TeamName": 7},
        ),
        (
            main_module.get_nhl_goaltending_wins_leaders,
            {"TeamName": 7},
            [_wins_row()],
            "wins",
            4,
            {"TeamName": 7},
        ),
        (
            main_module.get_nhl_playoff_schedule_games,
            {},
            [_schedule_row()],
            "seriesTitle",
            "Stanley Cup Final",
            None,
        ),
    ],
    ids=[
        "get_nhl_teams_success",
        "get_nhl_goal_leaders_success",
        "get_nhl_plusminus_leaders_success",
        "get_nhl_points_leaders_success",
        "get_nhl_goaltending_save_percentage_leaders_success",
        "get_nhl_goaltending_gaa_leaders_success",
        "get_nhl_goaltending_wins_leaders_success",
        "get_nhl_playoff_schedule_games_success",
    ],
)
def test_main_helpers_success(
    func,
    kwargs,
    rows,
    expected_attr,
    expected_value,
    expected_params,
):
    mock_session = MagicMock()
    mock_session.execute.return_value = _result_with_rows(rows)

    result = func(mock_session, **kwargs)

    assert len(result) == 1
    assert getattr(result[0], expected_attr) == expected_value
    mock_session.execute.assert_called_once()

    call_args = mock_session.execute.call_args[0]
    if expected_params is None:
        assert len(call_args) == 1
    else:
        assert call_args[1] == expected_params


@pytest.mark.unit
@pytest.mark.parametrize(
    "func, kwargs",
    [
        (main_module.get_nhl_teams, {}),
        (main_module.get_nhl_goal_leaders, {"TeamName": 7}),
        (main_module.get_nhl_plusminus_leaders, {"TeamName": 7}),
        (main_module.get_nhl_points_leaders, {"TeamName": 7}),
        (main_module.get_nhl_goaltending_save_percentage_leaders, {"TeamName": 7}),
        (main_module.get_nhl_goaltending_gaa_leaders, {"TeamName": 7}),
        (main_module.get_nhl_goaltending_wins_leaders, {"TeamName": 7}),
        (main_module.get_nhl_playoff_schedule_games, {}),
    ],
    ids=[
        "get_nhl_teams_failure",
        "get_nhl_goal_leaders_failure",
        "get_nhl_plusminus_leaders_failure",
        "get_nhl_points_leaders_failure",
        "get_nhl_goaltending_save_percentage_leaders_failure",
        "get_nhl_goaltending_gaa_leaders_failure",
        "get_nhl_goaltending_wins_leaders_failure",
        "get_nhl_playoff_schedule_games_failure",
    ],
)
def test_main_helpers_failure(func, kwargs):
    mock_session = MagicMock()
    mock_session.execute.side_effect = RuntimeError("db error")

    with pytest.raises(RuntimeError, match="db error"):
        func(mock_session, **kwargs)
