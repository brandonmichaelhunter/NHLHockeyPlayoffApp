import json
from unittest.mock import MagicMock

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import Column, Integer, String, text
from sqlalchemy.orm import declarative_base
from sqlmodel import Session, create_engine
from starlette.requests import Request

# from . import main as main_module
# from .main import get_nhl_goaltending_gaa_leaders
from src.api.hockeyplayoffapi import main as main_module
from src.api.hockeyplayoffapi.main import get_nhl_goaltending_gaa_leaders
Base = declarative_base()


class TestNHLScore(Base):
    __tablename__ = "nhl_scores"

    id = Column(Integer, primary_key=True)
    date = Column(String, nullable=False)
    home_team = Column(String, nullable=False)
    away_team = Column(String, nullable=False)


def _decode_json_response(response):
    return json.loads(response.body.decode("utf-8"))


def _create_schema(engine):
    with engine.begin() as conn:
        conn.exec_driver_sql(
            """
            CREATE TABLE teams (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                abbrv TEXT NOT NULL,
                logo_url TEXT NOT NULL
            )
            """
        )
        conn.exec_driver_sql(
            """
            CREATE TABLE players (
                id INTEGER PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                headshot_url TEXT NOT NULL
            )
            """
        )
        conn.exec_driver_sql(
            """
            CREATE TABLE team_roster (
                player_id INTEGER NOT NULL,
                team_id INTEGER NOT NULL
            )
            """
        )
        conn.exec_driver_sql(
            """
            CREATE TABLE games (
                id INTEGER PRIMARY KEY,
                year INTEGER NOT NULL,
                month INTEGER NOT NULL,
                day INTEGER NOT NULL
            )
            """
        )
        conn.exec_driver_sql(
            """
            CREATE TABLE player_game_stats (
                "gameID" INTEGER NOT NULL,
                "playerID" INTEGER NOT NULL,
                position TEXT NOT NULL,
                goals INTEGER DEFAULT 0,
                "plusMinus" INTEGER DEFAULT 0,
                points INTEGER DEFAULT 0,
                "savePctg" REAL,
                "goalsAgainst" INTEGER,
                toi TEXT
            )
            """
        )
        conn.exec_driver_sql(
            """
            CREATE TABLE goalie_wins_leaders (
                player_id INTEGER NOT NULL,
                wins INTEGER NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                headshot_url TEXT NOT NULL,
                team_name TEXT NOT NULL,
                team_abbrv TEXT NOT NULL,
                teamlogo_url TEXT NOT NULL,
                team_id INTEGER NOT NULL
            )
            """
        )
        conn.exec_driver_sql(
            """
            CREATE TABLE nhl_playoff_schedule_games (
                game_date TEXT NOT NULL,
                start_time TEXT NOT NULL,
                "awayTeamID" INTEGER NOT NULL,
                "awayTeamScore" INTEGER NOT NULL,
                "homeTeamId" INTEGER NOT NULL,
                "homeTeamScore" INTEGER NOT NULL,
                seriesTitle TEXT NOT NULL,
                "round" TEXT NOT NULL,
                stationinfo TEXT NOT NULL,
                "venueName" TEXT NOT NULL,
                "winningGoaliePlayerID" INTEGER NOT NULL,
                "winningGoalScorerPlayerID" INTEGER NOT NULL,
                series_info TEXT NOT NULL
            )
            """
        )


def _seed_data(engine):
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO teams (id, name, abbrv, logo_url) VALUES
                (7, 'Edmonton Oilers', 'EDM', 'https://example.com/edm.svg'),
                (8, 'Florida Panthers', 'FLA', 'https://example.com/fla.svg'),
                (9, 'Carolina Hurricanes', 'CAR', 'https://example.com/car.svg'),
                (54, 'Vegas Golden Knights', 'VGK', 'https://example.com/vgk.svg')
                """
            )
        )
        conn.execute(
            text(
                """
                INSERT INTO players (id, first_name, last_name, headshot_url) VALUES
                (1, 'Connor', 'McDavid', 'https://example.com/mcdavid.png'),
                (2, 'Aleksander', 'Barkov', 'https://example.com/barkov.png'),
                (3, 'Stuart', 'Skinner', 'https://example.com/skinner.png'),
                (4, 'Sergei', 'Bobrovsky', 'https://example.com/bobrovsky.png'),
                (5, 'Carter', 'Hart', 'https://example.com/hart.png'),
                (6, 'Shea', 'Theodore', 'https://example.com/theodore.png')
                """
            )
        )
        conn.execute(
            text(
                """
                INSERT INTO team_roster (player_id, team_id) VALUES
                (1, 7),
                (2, 8),
                (3, 7),
                (4, 8),
                (5, 54),
                (6, 54)
                """
            )
        )
        conn.execute(
            text(
                """
                INSERT INTO games (id, year, month, day) VALUES
                (100, 2026, 4, 20),
                (101, 2026, 5, 10),
                (102, 2026, 4, 21),
                (103, 2026, 5, 11)
                """
            )
        )
        conn.execute(
            text(
                """
                INSERT INTO player_game_stats
                ("gameID", "playerID", position, goals, "plusMinus", points, "savePctg", "goalsAgainst", toi)
                VALUES
                (100, 1, 'C', 2, 1, 3, NULL, NULL, NULL),
                (101, 1, 'C', 2, 2, 4, NULL, NULL, NULL),
                (102, 2, 'C', 1, 3, 4, NULL, NULL, NULL),
                (103, 2, 'C', 1, 1, 5, NULL, NULL, NULL),
                (100, 3, 'G', 0, 0, 0, 0.950, 2, '60:00'),
                (101, 3, 'G', 0, 0, 0, 0.930, 1, '58:30'),
                (102, 4, 'G', 0, 0, 0, 0.930, 3, '60:00'),
                (103, 4, 'G', 0, 0, 0, 0.940, 2, '59:00')
                """
            )
        )
        conn.execute(
            text(
                """
                INSERT INTO goalie_wins_leaders
                (player_id, wins, first_name, last_name, headshot_url, team_name, team_abbrv, teamlogo_url, team_id)
                VALUES
                (3, 3, 'Stuart', 'Skinner', 'https://example.com/skinner.png', 'Edmonton Oilers', 'EDM', 'https://example.com/edm.svg', 7),
                (4, 2, 'Sergei', 'Bobrovsky', 'https://example.com/bobrovsky.png', 'Florida Panthers', 'FLA', 'https://example.com/fla.svg', 8)
                """
            )
        )
        conn.execute(
            text(
                """
                INSERT INTO nhl_playoff_schedule_games
                (game_date, start_time, "awayTeamID", "awayTeamScore", "homeTeamId", "homeTeamScore",
                 seriesTitle, "round", stationinfo, "venueName", "winningGoaliePlayerID",
                 "winningGoalScorerPlayerID", series_info)
                VALUES
                (
                    '2026-06-06',
                    '2026-06-07T00:00:00Z',
                    9,
                    4,
                    54,
                    5,
                    'Stanley Cup Final',
                    '4',
                    'ABC',
                    'T-Mobile Arena',
                    5,
                    6,
                    'VGK leads series 2-1'
                )
                """
            )
        )
        conn.execute(
            text(
                """
                INSERT INTO nhl_scores (id, date, home_team, away_team) VALUES
                (1, '2026-06-06', 'VGK', 'CAR'),
                (2, '2026-06-05', 'FLA', 'EDM')
                """
            )
        )


@pytest.fixture()
def test_engine(tmp_path, monkeypatch):
    db_path = tmp_path / "test_main.sqlite"
    engine = create_engine(f"sqlite:///{db_path}", echo=False)

    monkeypatch.setattr(main_module, "engine", engine)
    monkeypatch.setattr(main_module, "nhl_scores", TestNHLScore)

    Base.metadata.create_all(engine)
    _create_schema(engine)
    _seed_data(engine)

    def override_get_session():
        with Session(engine) as session:
            yield session

    main_module.app.dependency_overrides[main_module.get_session] = override_get_session
    yield engine
    main_module.app.dependency_overrides.clear()


@pytest.fixture()
def db_session(test_engine):
    with Session(test_engine) as session:
        yield session

@pytest.mark.api
@pytest.mark.integration
def test_on_startup_calls_create_all(monkeypatch, test_engine):
    create_all_mock = MagicMock()
    monkeypatch.setattr(main_module.SQLModel.metadata, "create_all", create_all_mock)

    main_module.on_startup()

    create_all_mock.assert_called_once_with(test_engine)

@pytest.mark.api
@pytest.mark.integration
def test_get_session_yields_real_sqlmodel_session(test_engine):
    session_generator = main_module.get_session()
    session = next(session_generator)

    try:
        assert isinstance(session, Session)
        assert session.execute(text("SELECT 1")).scalar_one() == 1
    finally:
        session_generator.close()

@pytest.mark.api
@pytest.mark.integration
@pytest.mark.anyio
async def test_check_database_connection_uses_separate_sqlite_db(test_engine):
    assert await main_module.check_database_connection() is True

@pytest.mark.api
@pytest.mark.integration
def test_get_nhl_goaltending_gaa_leaders_filters_by_team(db_session):
    results = get_nhl_goaltending_gaa_leaders(db_session, TeamName=7)

    assert len(results) == 2
    assert all(row.player_id == 3 for row in results)
    assert all(row.team_name == "Edmonton Oilers" for row in results)
    assert results[0].gaa <= results[1].gaa
    assert pytest.approx(results[0].gaa, rel=1e-3) == 1.03
    assert pytest.approx(results[1].gaa, rel=1e-3) == 2.00

@pytest.mark.api
@pytest.mark.integration
def test_get_nhl_goaltending_gaa_leaders_without_team_filter(db_session):
    results = get_nhl_goaltending_gaa_leaders(db_session)

    assert len(results) == 4
    assert results[0].gaa <= results[-1].gaa
    assert {row.player_id for row in results} == {3, 4}

@pytest.mark.api
@pytest.mark.integration
@pytest.mark.parametrize(
    ("func", "kwargs", "expected_attr", "expected_value"),
    [
        (main_module.get_nhl_teams, {}, "team_name", "Carolina Hurricanes"),
        (main_module.get_nhl_goal_leaders, {"TeamName": 7}, "player_firstname", "Connor"),
        (main_module.get_nhl_plusminus_leaders, {"TeamName": 8}, "player_lastname", "Barkov"),
        (main_module.get_nhl_points_leaders, {}, "player_id", 2),
        (main_module.get_nhl_goaltending_save_percentage_leaders, {}, "player_id", 3),
        (main_module.get_nhl_goaltending_wins_leaders, {}, "player_id", 3),
        (main_module.get_nhl_playoff_schedule_games, {}, "seriesTitle", "Stanley Cup Final"),
    ],
    ids=[
        "teams",
        "goal-leaders",
        "plusminus-leaders",
        "points-leaders",
        "save-percentage-leaders",
        "wins-leaders",
        "playoff-schedule",
    ],
)
def test_helper_functions_with_real_sqlite_data(
    db_session,
    func,
    kwargs,
    expected_attr,
    expected_value,
):
    results = func(db_session, **kwargs)

    assert results
    assert getattr(results[0], expected_attr) == expected_value

@pytest.mark.api
@pytest.mark.integration
@pytest.mark.anyio
async def test_read_nhl_scores_returns_json_with_real_sqlite_data(db_session):
    request = Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/nhl_scores",
            "headers": [],
        }
    )

    response = await main_module.read_nhl_scores(
        session=db_session,
        request=request,
        hx_request="false",
        nhlScoreDateSelect="2026-06-06",
    )

    payload = _decode_json_response(response)

    assert response.status_code == 200
    assert payload == [
        {
            "id": 1,
            "date": "2026-06-06",
            "home_team": "VGK",
            "away_team": "CAR",
        }
    ]

@pytest.mark.api
@pytest.mark.integration
def test_get_avaliable_nhl_playoff_game_dates_returns_descending_dates(db_session):
    response = main_module.get_avaliable_nhl_playoff_game_dates(db_session)
    payload = _decode_json_response(response)

    assert response.status_code == 200
    assert payload == [
        {"date": "2026-06-06"},
        {"date": "2026-06-05"},
    ]


@pytest.mark.api
@pytest.mark.integration
@pytest.mark.anyio
async def test_main_routes_with_separate_sqlite_db(test_engine):
    async with AsyncClient(
        transport=ASGITransport(app=main_module.app),
        base_url="http://testserver",
    ) as client:
        response = await client.get("/health/live")
        assert response.status_code == 200
        assert response.json() == {"status": "alive"}

        response = await client.get("/health/ready")
        assert response.status_code == 200
        assert response.text == '"Database connection successful"'

        response = await client.get("/appname")
        assert response.status_code == 200
        assert response.json() == {"app_name": "Hockey Playoff API"}

        response = await client.get("/items/42", params={"q": "playoffs"})
        assert response.status_code == 200
        assert response.json() == {"item_id": 42, "q": "playoffs"}

        response = await client.get("/")
        assert response.status_code == 200

        response = await client.get("/stats")
        assert response.status_code == 200

        response = await client.get("/schedule")
        assert response.status_code == 200

        response = await client.get(
            "/nhl_scores",
            params={"nhlScoreDateSelect": "2026-06-06"},
            headers={"hx-request": "false"},
        )
        assert response.status_code == 200
        assert response.json()[0]["date"] == "2026-06-06"

        response = await client.get(
            "/nhl_scores",
            params={"nhlScoreDateSelect": "2026-06-06"},
            headers={"hx-request": "true"},
        )
        assert response.status_code == 200

        response = await client.get("/get_playoff_game_dates")
        assert response.status_code == 200
        assert response.json()[0]["date"] == "2026-06-06"

        response = await client.get("/get_nhl_schedule")
        assert response.status_code == 200

        response = await client.get("/get_nhl_teams")
        assert response.status_code == 200

        response = await client.get("/get_nhl_stats", params={"teams": 7})
        assert response.status_code == 200

# import pytest
# from httpx import ASGITransport, AsyncClient
# from src.api.hockeyplayoffapi.main import app
# from unittest.mock import MagicMock, patch
# from sqlmodel import Field, Session, SQLModel, create_engine, select
# from fastapi import HTTPException
# from src.api.hockeyplayoffapi.models.nhl_scores import nhl_scores
# from src.api.hockeyplayoffapi import main as main_module
# from fastapi.responses import HTMLResponse, JSONResponse

# @pytest.mark.integration
# @pytest.mark.anyio
# async def test_health_live():
#     async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost") as ac:
#         response = await ac.get("/health/live")

#     assert response.status_code == 200
#     assert response.json() == {"status": "alive"}

# @pytest.mark.integration
# @pytest.mark.anyio
# async def test_health_ready_db_connection():
#     async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost") as ac:
#         response = await ac.get("/health/ready")

#     assert response.status_code == 200
#     assert response.text == '"Database connection successful"'

# @pytest.mark.integration
# @pytest.mark.anyio
# async def test_read_nhl_scores_returns_html_with_hx_header_equal_false(tmp_path):
#           # set db paht to test database.
#           test_db_file = tmp_path / "test_nhl_db.db"
#           # create a test engine use to create the test database.
#           test_engine = create_engine(f"sqlite:///{test_db_file}")
#           # set the app engine with a local one.
#           main_module.engine = test_engine

#           try:
#               # create the test tables in our test database.
#               SQLModel.metadata.create_all(test_engine)
#               with Session(test_engine) as dbSession:
#                    dbSession.add(nhl_scores(date="2024-05-01", home_team="Rangers", home_team_image="home.png", away_team="Bruins", away_team_image="away.png"))
#                    dbSession.add(nhl_scores(date="2024-05-01", home_team="Leafs", home_team_image="home.png", away_team="Canadiens", away_team_image="away.png"))
#                    dbSession.commit()

#               # call the api.
#               async with AsyncClient(transport=ASGITransport(app=main_module.app), base_url="http://localhost") as ac:
#                    response = await ac.get("/nhl_scores", params={"nhlScoreDateSelect": "2024-05-01"}, headers={"hx-request": "false"})

#               # assertons
#               assert response.status_code == 200
#               assert "application/json" in response.headers["content-type"]

#           finally:
#               main_module.engine = None

# @pytest.mark.integration
# @pytest.mark.anyio
# async def test_read_nhl_scores_integration_returns_html_for_hx(tmp_path):
#     db_file = tmp_path / "test_scores_hx.db" # set path to db file.
#     test_engine = create_engine(f"sqlite:///{db_file}") # create sqlite engine with db path.
#     original_engine = main_module.engine
#     main_module.engine = test_engine #  set the app engine with a local one.

#     try:
#         SQLModel.metadata.create_all(test_engine) # create test tables in our test database.
#         with Session(test_engine) as s: # add test data to the test database.
#             s.add(
#                 nhl_scores(
#                     date="2024-05-01",
#                     home_team="Rangers",
#                     home_team_image="home.png",
#                     away_team="Bruins",
#                     away_team_image="away.png",
#                 )
#             )
#             s.commit()

#         async with AsyncClient(transport=ASGITransport(app=main_module.app),base_url="http://localhost") as ac:
#             response = await ac.get(
#                 "/nhl_scores",
#                 params={"nhlScoreDateSelect": "2024-05-01"},
#                 headers={"hx-request": "true"},
#             )

#         assert response.status_code == 200
#         assert "text/html" in response.headers["content-type"]
#         assert "Rangers" in response.text
#         assert "Bruins" in response.text
#     finally:
#         main_module.engine = original_engine
