from src.api.hockeyplayoffapi.models.nhl_scores import nhl_scores

from src.api.hockeyplayoffapi.models.nhl_stats import nhl_plusminus_leaders
from src.api.hockeyplayoffapi.models.nhl_stats import nhl_points_leaders
from src.api.hockeyplayoffapi.models.nhl_stats import (
    nhl_goaltending_save_percentage_leaders,
)
from src.api.hockeyplayoffapi.models.nhl_stats import nhl_goaltending_gaa_leaders
from src.api.hockeyplayoffapi.models.nhl_stats import nhl_goaltending_wins_leaders
from src.api.hockeyplayoffapi.models.nhl_schedules import nhl_playoff_schedule
from src.api.hockeyplayoffapi.models.nhl_stats import nhl_goal_leaders
import os
from typing import Optional
from src.api.hockeyplayoffapi.models.nhl_teams import nhl_playoff_dates, teams
from sqlmodel import create_engine
from .sqlmodel_manager import SQLModelDBManager


def get_engine(database_url: Optional[str] = None, **engine_kwargs):
    """Build an SQLAlchemy engine from DATABASE_URL or a sensible default.

    If `database_url` is not provided it will read `DATABASE_URL` from the
    environment. If that is not set, default to a file-based SQLite inside
    the repo (useful for local API runs).
    """
    database_url = (database_url or os.getenv("DATABASE_URL") or "").strip()
    database_url = database_url.strip('"').strip("'")
    print(f"Using database URL: {database_url}")
    if not database_url:
        print("Warning: DATABASE_URL not set, defaulting to local SQLite database.")
        repo_root = os.path.abspath(os.getcwd())
        default = (
            f"sqlite:///{os.path.join(repo_root, 'src', 'data', 'hockeyplayoff.db')}"
        )
        database_url = default
    return create_engine(database_url, **engine_kwargs)


def get_db_manager(engine=None, **engine_kwargs) -> SQLModelDBManager:
    """Return an instance of `SQLModelDBManager`, creating an engine if needed."""
    if engine is None:
        engine = get_engine(**engine_kwargs)
    return SQLModelDBManager(engine)


class DBManagerFactory:
    """Factory class to create DB manager instances."""

    dbContext: Optional[SQLModelDBManager] = None

    def __init__(self, engine=None, **engine_kwargs):
        # ensure instance has a DB manager
        self.dbContext = get_db_manager(engine=engine, **engine_kwargs)

    @staticmethod
    def create_db_manager(engine=None, **engine_kwargs) -> SQLModelDBManager:
        """Create and return an instance of `SQLModelDBManager`."""
        return get_db_manager(engine=engine, **engine_kwargs)

    def get_playoff_game_dates(self) -> list[nhl_playoff_dates]:
        if self.dbContext is None:
            raise ValueError("DB context has not be initialized.")

        rows = self.dbContext.execute_fetch(
            "select distinct date from nhl_scores order by date desc"
        )
        gameDates: list[nhl_playoff_dates] = [nhl_playoff_dates(**row) for row in rows]
        return gameDates

    def get_read_nhl_scores(self, nhlScoreDateSelect: str) -> list[nhl_scores]:
        if self.dbContext is None:
            raise ValueError("DB context has not be initialized.")

        rows = self.dbContext.execute_fetch(
            "select * from nhl_scores where date = :nhlScoreDateSelect",
            nhlScoreDateSelect=nhlScoreDateSelect,
        )
        nhlScores: list[nhl_scores] = [nhl_scores(**row) for row in rows]

        return nhlScores

    def get_nhl_teams_data(self) -> list[teams]:
        if self.dbContext is None:
            raise ValueError("DB context has not be initialized.")

        rows = self.dbContext.execute_fetch(
            "select id, name as team_name from teams order by name"
        )
        teamList: list[teams] = [teams(**row) for row in rows]
        return teamList

    def get_nhl_goal_leaders(self, TeamName: int = 0) -> list[nhl_goal_leaders]:
        # print(f"Getting NHL Goal Leaders for Team: {TeamName}")
        if self.dbContext is None:
            raise ValueError("DB context has not be initialized.")

        if TeamName != 0:
            rows = self.dbContext.execute_fetch(
                """
                            select distinct playerID as player_id, Sum(goals) as total_goals,
                                RANK() OVER (ORDER BY SUM(goals) desc) as league_ranking,
                                b.first_name as player_firstname, b.last_name  as player_lastname,
                                b.headshot_url as player_headshot,a.position as player_position,
                                d.name as team_name, d.abbrv as team_abbrv, d.logo_url as team_logo
                            from player_game_stats a inner join players b on b.id = a.playerID
                                                                                inner join team_roster c on c.player_id = b.id
                                                                                inner join teams d on d.id = c.team_id
                            where a.position in ('L','R','C','D') and d.id = :TeamName and (gameID in (select id from games where year = 2026 and month in (4) and day > 15) or
                                        gameID in (select id from games where year = 2026 and month in (5)) )
                            group by playerID, goals
                            order by total_goals  desc
                            limit 5
                    """,
                TeamName=TeamName,
            )
        else:
            rows = self.dbContext.execute_fetch(
                """
                            select distinct playerID as player_id, Sum(goals) as total_goals,
                                RANK() OVER (ORDER BY SUM(goals) desc) as league_ranking,
                                b.first_name as player_firstname, b.last_name  as player_lastname,
                                b.headshot_url as player_headshot,a.position as player_position,
                                d.name as team_name, d.abbrv as team_abbrv, d.logo_url as team_logo
                            from player_game_stats a inner join players b on b.id = a.playerID
                                                                                inner join team_roster c on c.player_id = b.id
                                                                                inner join teams d on d.id = c.team_id
                            where a.position in ('L','R','C','D') and (gameID in (select id from games where year = 2026 and month in (4) and day > 15) or
                                        gameID in (select id from games where year = 2026 and month in (5)) )
                            group by playerID, goals
                            order by total_goals  desc
                            limit 5
                    """
            )
        return [nhl_goal_leaders(**row) for row in rows]

    def get_nhl_plusminus_leaders(
        self, TeamName: int = 0
    ) -> list[nhl_plusminus_leaders]:
        if self.dbContext is None:
            raise ValueError("DB manager has not been initialized.")

        if TeamName != 0:
            rows = self.dbContext.execute_fetch(
                """
                            select distinct playerID as player_id, Sum(plusMinus) as plus_minus,
                                RANK() OVER (ORDER BY SUM(plusMinus) desc) as league_ranking,
                                b.first_name as player_firstname, b.last_name  as player_lastname,
                                b.headshot_url as player_headshot,a.position as player_position,
                                d.name as team_name, d.abbrv as team_abbrv, d.logo_url as team_logo
                            from player_game_stats a inner join players b on b.id = a.playerID
                                                                                inner join team_roster c on c.player_id = b.id
                                                                                inner join teams d on d.id = c.team_id
                            where a.position in ('L','R','C','D') and d.id = :TeamName and (gameID in (select id from games where year = 2026 and month in (4) and day > 15) or
                                        gameID in (select id from games where year = 2026 and month in (5)) )
                            group by playerID
                            order by plus_minus  desc
                            limit 5
                    """,
                TeamName=TeamName,
            )
        else:
            rows = self.dbContext.execute_fetch(
                """
                            select distinct playerID as player_id, Sum(plusMinus) as plus_minus,
                                RANK() OVER (ORDER BY SUM(plusMinus) desc) as league_ranking,
                                b.first_name as player_firstname, b.last_name  as player_lastname,
                                b.headshot_url as player_headshot,a.position as player_position,
                                d.name as team_name, d.abbrv as team_abbrv, d.logo_url as team_logo
                            from player_game_stats a inner join players b on b.id = a.playerID
                                                                                inner join team_roster c on c.player_id = b.id
                                                                                inner join teams d on d.id = c.team_id
                            where a.position in ('L','R','C','D') and (gameID in (select id from games where year = 2026 and month in (4) and day > 15) or
                                        gameID in (select id from games where year = 2026 and month in (5)) )
                            group by playerID
                            order by plus_minus  desc
                            limit 5
                    """
            )
        return [nhl_plusminus_leaders(**row) for row in rows]

    def get_nhl_points_leaders(self, TeamName: int = 0) -> list[nhl_points_leaders]:
        if self.dbContext is None:
            raise ValueError("DB manager has not been initialized.")

        if TeamName != 0:
            rows = self.dbContext.execute_fetch(
                """
                            select distinct playerID as player_id, Sum(a.points) as total_points,
                                RANK() OVER (ORDER BY SUM(a.points) desc) as league_ranking,
                                b.first_name as player_firstname, b.last_name  as player_lastname,
                                b.headshot_url as player_headshot,a.position as player_position,
                                d.name as team_name, d.abbrv as team_abbrv, d.logo_url as team_logo
                            from player_game_stats a inner join players b on b.id = a.playerID
                                                                                inner join team_roster c on c.player_id = b.id
                                                                                inner join teams d on d.id = c.team_id
                            where a.position in ('L','R','C','D') and d.id = :TeamName and (gameID in (select id from games where year = 2026 and month in (4) and day > 15) or
                                        gameID in (select id from games where year = 2026 and month in (5)) )
                            group by playerID
                            order by total_points  desc
                            limit 5
                    """,
                TeamName=TeamName,
            )
        else:
            rows = self.dbContext.execute_fetch(
                """
                            select distinct playerID as player_id, Sum(a.points) as total_points,
                                RANK() OVER (ORDER BY SUM(a.points) desc) as league_ranking,
                                b.first_name as player_firstname, b.last_name  as player_lastname,
                                b.headshot_url as player_headshot,a.position as player_position,
                                d.name as team_name, d.abbrv as team_abbrv, d.logo_url as team_logo
                            from player_game_stats a inner join players b on b.id = a.playerID
                                                                                inner join team_roster c on c.player_id = b.id
                                                                                inner join teams d on d.id = c.team_id
                            where a.position in ('L','R','C','D') and (gameID in (select id from games where year = 2026 and month in (4) and day > 15) or
                                        gameID in (select id from games where year = 2026 and month in (5)) )
                            group by playerID
                            order by total_points  desc
                            limit 5
                    """
            )
        return [nhl_points_leaders(**row) for row in rows]

    def get_nhl_goaltending_save_percentage_leaders(
        self, TeamName: int = 0
    ) -> list[nhl_goaltending_save_percentage_leaders]:
        if self.dbContext is None:
            raise ValueError("DB manager has not been initialized.")

        if TeamName != 0:
            rows = self.dbContext.execute_fetch(
                """
                            select distinct playerID as player_id, (round(avg(a.savePctg),3)) as save_percentage,
                                RANK() OVER (ORDER BY round(avg(a.savePctg),3) desc) as league_ranking,
                                b.first_name as player_firstname, b.last_name  as player_lastname,
                                b.headshot_url as player_headshot,a.position as player_position,
                                d.name as team_name, d.abbrv as team_abbrv, d.logo_url as team_logo
                            from player_game_stats a inner join players b on b.id = a.playerID
                                                                                inner join team_roster c on c.player_id = b.id
                                                                                inner join teams d on d.id = c.team_id
                            where a.position in ('G') and d.id = :TeamName and (gameID in (select id from games where year = 2026 and month in (4) and day > 15) or
                                        gameID in (select id from games where year = 2026 and month in (5)) )
                            group by playerID
                            order by save_percentage  desc
                            limit 5
                    """,
                TeamName=TeamName,
            )
        else:
            rows = self.dbContext.execute_fetch(
                """
                            select distinct playerID as player_id, (round(avg(a.savePctg),3)) as save_percentage,
                                RANK() OVER (ORDER BY (round(avg(a.savePctg),3))  desc) as league_ranking,
                                b.first_name as player_firstname, b.last_name  as player_lastname,
                                b.headshot_url as player_headshot,a.position as player_position,
                                d.name as team_name, d.abbrv as team_abbrv, d.logo_url as team_logo
                            from player_game_stats a inner join players b on b.id = a.playerID
                                                                                inner join team_roster c on c.player_id = b.id
                                                                                inner join teams d on d.id = c.team_id
                            where a.position in ('G') and (gameID in (select id from games where year = 2026 and month in (4) and day > 15) or
                                        gameID in (select id from games where year = 2026 and month in (5)) )
                            group by playerID
                            order by save_percentage  desc
                            limit 5
                    """
            )
        return [nhl_goaltending_save_percentage_leaders(**row) for row in rows]

    def get_nhl_goaltending_gaa_leaders(
        self, TeamName: int = 0
    ) -> list[nhl_goaltending_gaa_leaders]:
        if self.dbContext is None:
            raise ValueError("DB manager has not been initialized.")
        if TeamName != 0:
            rows = self.dbContext.execute_fetch(
                """
                            select distinct playerID as player_id,
                            avg(ROUND((goalsAgainst * 60) / ROUND((CAST(SUBSTR(toi, 1, 2) AS REAL) +  (CAST(SUBSTR(toi, 4, 2) AS REAL) / 60.0) ),2) , 2)) as gaa,
                            RANK() OVER (ORDER BY avg(ROUND((goalsAgainst * 60) / ROUND((CAST(SUBSTR(toi, 1, 2) AS REAL) +  (CAST(SUBSTR(toi, 4, 2) AS REAL) / 60.0) ),2) , 2))  asc) as league_ranking,
                                                        b.first_name as player_firstname, b.last_name  as player_lastname,
                            b.headshot_url as player_headshot,
                            a.position as player_position,
                            d.name as team_name,
                            d.abbrv as team_abbrv,
                            d.logo_url as team_logo
                            from player_game_stats a inner join players b on b.id = a.playerID
                                                                                inner join team_roster c on c.player_id = b.id
                                                                                inner join teams d on d.id = c.team_id
                            where a.position in ('G') and d.id = :TeamName and (gameID in (select id from games where year = 2026 and month in (4) and day > 15) or
                                        gameID in (select id from games where year = 2026 and month in (5)) ) and
                                        ROUND((CAST(SUBSTR(toi, 1, 2) AS REAL) +  (CAST(SUBSTR(toi, 4, 2) AS REAL) / 60.0) ),2) > 1
                            group by gameID
                            order by gaa  asc
                            limit 5
                            """,
                TeamName=TeamName,
            )
        else:
            rows = self.dbContext.execute_fetch(
                """
                            select distinct playerID as player_id,
                            avg(ROUND((goalsAgainst * 60) / ROUND((CAST(SUBSTR(toi, 1, 2) AS REAL) +  (CAST(SUBSTR(toi, 4, 2) AS REAL) / 60.0) ),2) , 2)) as gaa,
                            RANK() OVER (ORDER BY avg(ROUND((goalsAgainst * 60) / ROUND((CAST(SUBSTR(toi, 1, 2) AS REAL) +  (CAST(SUBSTR(toi, 4, 2) AS REAL) / 60.0) ),2) , 2))  asc) as league_ranking,
                                                        b.first_name as player_firstname, b.last_name  as player_lastname,
                            b.headshot_url as player_headshot,
                            a.position as player_position,
                            d.name as team_name,
                            d.abbrv as team_abbrv,
                            d.logo_url as team_logo
                            from player_game_stats a inner join players b on b.id = a.playerID
                                                                                inner join team_roster c on c.player_id = b.id
                                                                                inner join teams d on d.id = c.team_id
                            where a.position in ('G') and (gameID in (select id from games where year = 2026 and month in (4) and day > 15) or
                                        gameID in (select id from games where year = 2026 and month in (5)) ) and
                                        ROUND((CAST(SUBSTR(toi, 1, 2) AS REAL) +  (CAST(SUBSTR(toi, 4, 2) AS REAL) / 60.0) ),2) > 1
                            group by gameID
                            order by gaa  asc
                            limit 5
                            """
            )
        return [nhl_goaltending_gaa_leaders(**row) for row in rows]

    def get_nhl_goaltending_wins_leaders(
        self, TeamName: int = 0
    ) -> list[nhl_goaltending_wins_leaders]:
        if self.dbContext is None:
            raise ValueError("DB manager has not been initialized.")

        if TeamName != 0:
            rows = self.dbContext.execute_fetch(
                """
                            SELECT  gwl.player_id, gwl.wins,
                                    RANK() OVER (ORDER BY gwl.wins DESC) as league_ranking,
                                    gwl.first_name as player_firstname,
                                    gwl.last_name as player_lastname,
                                    gwl.headshot_url as player_headshot,
                                    'G' as player_position,
                                    gwl.team_name,
                                    gwl.team_abbrv,
                                    gwl.teamlogo_url as team_logo
                            FROM
                                goalie_wins_leaders gwl
                            WHERE gwl.team_id = :TeamName
                            ORDER BY
                                wins DESC
                            LIMIT 5;
                            """,
                TeamName=TeamName,
            )
        else:
            rows = self.dbContext.execute_fetch(
                """
                            SELECT gwl.player_id, gwl.wins,
                                    RANK() OVER (ORDER BY gwl.wins DESC) as league_ranking,
                                    gwl.first_name as player_firstname,
                                    gwl.last_name as player_lastname,
                                    gwl.headshot_url as player_headshot,
                                    'G' as player_position,
                                    gwl.team_name,
                                    gwl.team_abbrv,
                                    gwl.teamlogo_url as team_logo
                            FROM
                                goalie_wins_leaders gwl
                            ORDER BY
                                wins DESC
                            LIMIT 5;
                            """
            )
        return [nhl_goaltending_wins_leaders(**row) for row in rows]

    def get_nhl_playoff_schedule_games(self) -> list[nhl_playoff_schedule]:
        if self.dbContext is None:
            raise ValueError("DB manager has not been initialized.")

        rows = self.dbContext.execute_fetch(
            """
                            select distinct a.game_date as gameDate, a.start_time as gameStartTime,
                            away.name as awayTeamName, a.awayTeamScore as awayScore, away.abbrv as awayTeamNameAbbrv, away.logo_url as awayTeamLogoUrl,
                            home.name as homeTeamName, a.homeTeamScore as homeScore, home.abbrv as homeTeamNameAbbrv, home.logo_url as homeTeamLogoUrl,
                            a.seriesTitle as seriesTitle, a.round as playoffRound, a.stationinfo as tvStation,  a.venueName as homeTeamVenueName,
                            a.winningGoaliePlayerID, goalie.first_name as goalieFirstName, goalie.last_name as goalieLastName,  goalie.headshot_url as goalieHeadShotUrl,
                            a.winningGoalScorerPlayerID, skater.first_name as skaterFirstName, skater.last_name as skaterLastName, skater.headshot_url as skaterHeadShotUrl,
                            a.series_info as  seriesInfo
                            from nhl_playoff_schedule_games a inner join teams home on home.id = a.homeTeamId
                                                                                                    inner join teams away on away.id = a.awayTeamID
                                                                                                    inner join players goalie on goalie.id = a.winningGoaliePlayerID
                                                                                                    inner join players skater on skater.id = a.winningGoalScorerPlayerID
                            order by a.game_date desc ;
                            """
        )
        schedule: list[nhl_playoff_schedule] = [
            nhl_playoff_schedule(**row) for row in rows
        ]
        return schedule


# TODO: Move all select statement calls to this class and call them from the API client.
