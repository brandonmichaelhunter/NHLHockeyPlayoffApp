import pytest
from httpx import ASGITransport, AsyncClient
from src.api.hockeyplayoffapi.main import app
from sqlmodel import Session, create_engine, text
from src.api.hockeyplayoffapi import main as main_module
from src.shared.db.factory import DBManagerFactory


def _seed_nhl_scores(engine, rows):
    with Session(engine) as session:
        # pyrefly: ignore [no-matching-overload]
        session.exec(
            text(
                """
                CREATE TABLE IF NOT EXISTS nhl_scores (
                    id INTEGER PRIMARY KEY,
                    date TEXT,
                    home_team TEXT,
                    home_team_image TEXT,
                    away_team TEXT,
                    away_team_image TEXT,
                    home_score INTEGER DEFAULT 0,
                    away_score INTEGER DEFAULT 0,
                    first_period_home_score INTEGER DEFAULT 0,
                    second_period_home_score INTEGER DEFAULT 0,
                    third_period_home_score INTEGER DEFAULT 0,
                    overtime_home_score INTEGER DEFAULT 0,
                    final_home_score INTEGER DEFAULT 0,
                    first_period_away_score INTEGER DEFAULT 0,
                    second_period_away_score INTEGER DEFAULT 0,
                    third_period_away_score INTEGER DEFAULT 0,
                    overtime_away_score INTEGER DEFAULT 0,
                    final_away_score INTEGER DEFAULT 0,
                    round TEXT DEFAULT '',
                    game_number INTEGER DEFAULT 0,
                    series_info TEXT DEFAULT ''
                )
                """
            )
        )
        for row in rows:
            # pyrefly: ignore [no-matching-overload]
            session.exec(
                text(
                    """
                    INSERT INTO nhl_scores (
                        date,
                        home_team,
                        home_team_image,
                        away_team,
                        away_team_image
                    ) VALUES (
                        :date,
                        :home_team,
                        :home_team_image,
                        :away_team,
                        :away_team_image
                    )
                    """
                ),
                params=dict(row),
            )
        session.commit()


@pytest.mark.api_integration
@pytest.mark.anyio
async def test_health_ready_db_connection():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://localhost"
    ) as ac:
        response = await ac.get("/health/ready")

    assert response.status_code == 200
    assert response.text == '"Database connection successful"'


@pytest.mark.api_integration
@pytest.mark.anyio
async def test_health_live():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://localhost"
    ) as ac:
        response = await ac.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


@pytest.mark.api_integration
@pytest.mark.anyio
async def test_read_nhl_scores_returns_json_with_hx_header_false(tmp_path):
    test_db_file = tmp_path / "test_nhl_db.db"
    test_engine = create_engine(f"sqlite:///{test_db_file}")
    original_db_manager = main_module.db_manager
    main_module.db_manager = DBManagerFactory(engine=test_engine)

    try:
        _seed_nhl_scores(
            test_engine,
            [
                {
                    "date": "2024-05-01",
                    "home_team": "Rangers",
                    "home_team_image": "home.png",
                    "away_team": "Bruins",
                    "away_team_image": "away.png",
                },
                {
                    "date": "2024-05-01",
                    "home_team": "Leafs",
                    "home_team_image": "home.png",
                    "away_team": "Canadiens",
                    "away_team_image": "away.png",
                },
            ],
        )

        async with AsyncClient(
            transport=ASGITransport(app=main_module.app), base_url="http://localhost"
        ) as ac:
            response = await ac.get(
                "/nhl_scores",
                params={"nhlScoreDateSelect": "2024-05-01"},
                headers={"hx-request": "false"},
            )

        assert response.status_code == 200
        assert "application/json" in response.headers["content-type"]
        payload = response.json()
        assert len(payload) == 2
        assert payload[0]["home_team"] in {"Rangers", "Leafs"}

    finally:
        main_module.db_manager = original_db_manager


@pytest.mark.api_integration
@pytest.mark.anyio
async def test_read_nhl_scores_integration_returns_html_for_hx(tmp_path):
    db_file = tmp_path / "test_scores_hx.db"
    test_engine = create_engine(f"sqlite:///{db_file}")
    original_db_manager = main_module.db_manager
    main_module.db_manager = DBManagerFactory(engine=test_engine)

    try:
        _seed_nhl_scores(
            test_engine,
            [
                {
                    "date": "2024-05-01",
                    "home_team": "Rangers",
                    "home_team_image": "home.png",
                    "away_team": "Bruins",
                    "away_team_image": "away.png",
                }
            ],
        )

        async with AsyncClient(
            transport=ASGITransport(app=main_module.app), base_url="http://localhost"
        ) as ac:
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
        main_module.db_manager = original_db_manager
