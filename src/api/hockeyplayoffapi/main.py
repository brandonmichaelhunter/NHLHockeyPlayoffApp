from functools import wraps
from typing import Annotated, Optional, Union
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, Header
from sqlmodel import create_engine
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.encoders import jsonable_encoder
import os
from pathlib import Path

from .models.nhl_schedules import nhl_playoff_schedule


from .models.nhl_teams import teams, nhl_playoff_dates
from .models.nhl_stats import (
    nhl_goal_leaders,
    nhl_goaltending_gaa_leaders,
    nhl_goaltending_save_percentage_leaders,
    nhl_goaltending_wins_leaders,
    nhl_points_leaders,
)

# if os.environ.get("DOCKER_ENV"):
# from api.hockeyplayoffapi.models.nhl_scores import nhl_scores
from .models.nhl_scores import nhl_scores

# else:
#    from src.api.hockeyplayoffapi.models.nhl_scores import nhl_scores
# Shared DB manager (SQLModel-backed) for higher-level operations
from shared.db.factory import DBManagerFactory
from typing import Any

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_BASE_DIR = Path(__file__).resolve().parent
# Create data directory if it doesn't exist
DB_DIR = os.path.join(BASE_DIR, "./data")
os.makedirs(DB_DIR, exist_ok=True)

DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, './data/hockeyplayoff.db')}"
engine = create_engine(DATABASE_URL, echo=True)


# instantiate adapter for use by API code (can be injected or accessed directly)
# Use a generic Any type for the runtime DB manager instance returned by the factory
db_manager: Optional[Any] = None


def inject_db(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Pass the global db_manager as the first argument,
        # followed by whatever arguments the function originally needed
        global db_manager
        if db_manager is None:
            raise ValueError("DB manager has not been initialized.")
        return func(db_manager, *args, **kwargs)

    return wrapper


app = FastAPI()

# used to attach static files to the API for serving HTML templates and static assets.
app.mount(
    "/static",
    StaticFiles(directory=str(Path(TEMPLATE_BASE_DIR, "templates"))),
    name="static",
)
# used to support rendering dynamic HTML template using Jinja1.
templates = Jinja2Templates(directory=str(Path(TEMPLATE_BASE_DIR, "templates")))


# manages the life cycle of the FastAPI application.
@asynccontextmanager
async def ManageLifecycle(app: FastAPI):
    try:
        global db_manager
        if db_manager is None:
            print("Initializing database once..", flush=True)
            db_manager = DBManagerFactory(engine=None)
        yield
        print("Shutting down application...", flush=True)
    except Exception as e:
        print(f"CRITICAL: Database initialization failed: {e}", flush=True)
        raise


# Initialize application
app = FastAPI(lifespan=ManageLifecycle)


@app.get("/health")
def health_check():
    return {"status": "alive"}


@app.get("/health/live")
async def healthlive():
    return {"status": "alive"}


async def check_database_connection():
    try:
        with engine.connect() as conn:
            if conn is not None:
                return True
            else:
                return False
    except Exception as e:
        print(f"Database connection error: {e}")
        return False


@app.get("/health/ready")
async def healthready():
    db_ok = await check_database_connection()
    if not db_ok:
        raise HTTPException(status_code=503, detail="Database connection failed")
    return "Database connection successful"


@app.get("/nhl_scores", response_class=HTMLResponse)
async def read_nhl_scores(
    request: Request,
    hx_request: Annotated[Union[str, None], Header()] = None,
    nhlScoreDateSelect: str = "",
):

    nhlScores = get_nhl_scores_by_date(nhlScoreDateSelect=nhlScoreDateSelect)

    if hx_request != "false":
        resp = templates.TemplateResponse(
            request=request, name="nhlscores.html", context={"nhlScores": nhlScores}
        )
        return resp
    return JSONResponse(content=jsonable_encoder(nhlScores))


@inject_db
def get_nhl_scores_by_date(db, nhlScoreDateSelect: str) -> list[nhl_scores]:
    return db.get_read_nhl_scores(nhlScoreDateSelect=nhlScoreDateSelect)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/stats", response_class=HTMLResponse)
async def nhl_stats(request: Request):
    return templates.TemplateResponse(request=request, name="stats.html", context={})


@app.get("/schedule", response_class=HTMLResponse)
async def nhl_schedule(request: Request):
    return templates.TemplateResponse(request=request, name="schedule.html", context={})


@app.get("/get_nhl_schedule", response_class=HTMLResponse)
async def get_nhl_schedule(request: Request):
    nhlPlayoffSchedules: list[nhl_playoff_schedule] = get_nhl_playoff_schedule_games()
    return templates.TemplateResponse(
        request=request,
        name="nhl_schedule.html",
        context={"schedules": nhlPlayoffSchedules},
    )


@app.get("/get_nhl_teams", response_class=HTMLResponse)
async def get_nhl_teams(request: Request):
    teams = get_nhl_teams_data()
    return templates.TemplateResponse(
        request=request, name="nhl_teams_options.html", context={"teams": teams}
    )


@app.get("/get_nhl_stats", response_class=HTMLResponse)
async def get_nhl_stats(request: Request, teams: int = 0):
    print(f"Getting NHL Stats for Team: {teams}")
    playerGoalRanks = get_nhl_goal_leaders(TeamName=teams)
    playerPlusMinusRanks = get_nhl_plusminus_leaders(TeamName=teams)
    playerPointsRanks = get_nhl_points_leaders(TeamName=teams)
    goalieSavePercentageRanks = get_nhl_goaltending_save_percentage_leaders(
        TeamName=teams
    )
    goalieGAARanks = get_nhl_goaltending_gaa_leaders(TeamName=teams)
    goalieWins = get_nhl_goaltending_wins_leaders(TeamName=teams)
    return templates.TemplateResponse(
        request=request,
        name="nhlstats_leaders.html",
        context={
            "playerGoalRanks": playerGoalRanks,
            "playerPlusMinusRanks": playerPlusMinusRanks,
            "playerPointsRanks": playerPointsRanks,
            "goalieSavePercentageRanks": goalieSavePercentageRanks,
            "goalieGAARanks": goalieGAARanks,
            "goalieWinsRanks": goalieWins,
        },
    )


@app.get("/get_playoff_game_dates", response_class=JSONResponse)
def get_avaliable_nhl_playoff_game_dates() -> JSONResponse:
    global db_manager
    if db_manager is None:
        raise ValueError("DB manager has not been initialized.")

    gameDates: list[nhl_playoff_dates] = db_manager.get_playoff_game_dates()

    return JSONResponse(content=jsonable_encoder(gameDates))


def get_nhl_teams_data() -> list[teams]:
    if db_manager is None:
        raise ValueError("DB manager has not been initialized.")

    nhlTeams: list[teams] = db_manager.get_nhl_teams_data()

    return nhlTeams


def get_nhl_goal_leaders(TeamName: int = 0) -> list[nhl_goal_leaders]:
    print(f"Getting NHL Goal Leaders for Team: {TeamName}")
    global db_manager
    if db_manager is None:
        raise ValueError("DB manager has not been initialized.")

    return db_manager.get_nhl_goal_leaders(TeamName=TeamName)


@inject_db
def get_nhl_plusminus_leaders(db, TeamName: int = 0) -> list[nhl_goal_leaders]:
    return db.get_nhl_plusminus_leaders(TeamName=TeamName)


@inject_db
def get_nhl_points_leaders(db, TeamName: int = 0) -> list[nhl_points_leaders]:
    return db.get_nhl_points_leaders(TeamName=TeamName)


@inject_db
def get_nhl_goaltending_save_percentage_leaders(
    db, TeamName: int = 0
) -> list[nhl_goaltending_save_percentage_leaders]:
    return db.get_nhl_goaltending_save_percentage_leaders(TeamName=TeamName)


@inject_db
def get_nhl_goaltending_gaa_leaders(
    db, TeamName: int = 0
) -> list[nhl_goaltending_gaa_leaders]:

    return db.get_nhl_goaltending_gaa_leaders(TeamName=TeamName)
    # return [nhl_goaltending_gaa_leaders(**row) for row in rows]


def get_nhl_goaltending_wins_leaders(
    TeamName: int = 0,
) -> list[nhl_goaltending_wins_leaders]:

    global db_manager
    if db_manager is None:
        raise ValueError("DB manager has not been initialized.")

    return db_manager.get_nhl_goaltending_wins_leaders(TeamName=TeamName)


def get_nhl_playoff_schedule_games() -> list[nhl_playoff_schedule]:
    global db_manager
    if db_manager is None:
        raise ValueError("DB manager has not been initialized.")

    return db_manager.get_nhl_playoff_schedule_games()


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}


@app.get("/appname")
async def get_app_name():
    return {"app_name": "Hockey Playoff API"}
