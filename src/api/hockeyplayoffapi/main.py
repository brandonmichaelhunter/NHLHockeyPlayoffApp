from typing import Annotated, Union
from fastapi import Depends, FastAPI, HTTPException, Query, Request,Header
from httpx import request
from sqlmodel import Field, Session, SQLModel, create_engine, select, text
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
import os
from pathlib import Path
from .models.nhl_teams import nhl_teams, teams
from .models.nhl_stats import nhl_goal_leaders, nhl_goaltending_save_percentage_leaders, nhl_plusminus_leaders, nhl_points_leaders
print(f"Running in Docker: {os.environ.get('DOCKER_ENV')}")
if os.environ.get('DOCKER_ENV'):
   from api.hockeyplayoffapi.models.nhl_scores import nhl_scores
else:
   from src.api.hockeyplayoffapi.models.nhl_scores import nhl_scores

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_BASE_DIR = Path(__file__).resolve().parent

DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, './data/hockeyplayoff.db')}"
engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]
app = FastAPI()

templates = Jinja2Templates(directory=str(Path(TEMPLATE_BASE_DIR, "templates")))
#--------------------------------------------------------------------------------------
# select distinct playerID as player_id,
# Sum(goals) as total_goals,
# RANK() OVER (ORDER BY SUM(goals) desc) as league_ranking,
# b.first_name +' '+ b.last_name as player_fullname,
# b.headshot_url as player_headshot,
# a.position as player_position,
# d.name as team_name,
# d.abbrv as team_abbrv,
# d.logo_url as team_logo,
# from player_game_stats a inner join players b on b.id = a.playerID
# 												     inner join team_roster c on c.player_id = b.id
# 													 inner join teams d on d.id = c.team_id
#where a.position in ('L','R','C','D') and (gameID in (select id from games where year = 2026 and month in (4) and day > 15) or
#              gameID in (select id from games where year = 2026 and month in (5)) )
#group by playerID, goals
#order by total_goals  desc
#limit 5
#--------------------------------------------------------------------------------------
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

@app.get("/health/live")
async def healthlive():
    return {"status": "alive"}

async def check_database_connection():
          try:
                with engine.connect() as conn:
                     return True
          except:
                return False

@app.get("/health/ready")
async def healthready():
      db_ok = await check_database_connection()
      if not db_ok:
            raise HTTPException(status_code=503, detail="Database connection failed")
      return "Database connection successful"
@app.get("/nhl_scores", response_class=HTMLResponse)
async def read_nhl_scores(session: SessionDep, request: Request,  hx_request: Annotated[Union[str, None], Header()] = None, nhlScoreDateSelect:str=None):
    sqlStmt = select(nhl_scores).where(nhl_scores.date == nhlScoreDateSelect)
    nhlScores = session.exec(sqlStmt).all()

    if hx_request != "false":
       resp = templates.TemplateResponse(request=request, name="nhlscores.html", context={"nhlScores": nhlScores})
       return resp
    return JSONResponse(content=jsonable_encoder(nhlScores))

@app.get("/", response_class=HTMLResponse)
async def index(request:Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/stats", response_class=HTMLResponse)
async def nhl_stats(session: SessionDep, request:Request):
          return templates.TemplateResponse(request=request, name="stats.html", context={})

@app.get("/get_nhl_teams", response_class=HTMLResponse)
async def get_nhl_teams(session: SessionDep, request:Request):
          teams = get_nhl_teams(session=session)
          return templates.TemplateResponse(request=request, name="nhl_teams_options.html", context={"teams": teams})

@app.get("/get_nhl_stats", response_class=HTMLResponse)
async def get_nhl_stats(session: SessionDep, request:Request, teams: int=0):
          print(f"Getting NHL Stats for Team: {teams}")
          playerGoalRanks = get_nhl_goal_leaders(session=session, TeamName=teams)
          playerPlusMinusRanks = get_nhl_plusminus_leaders(session=session, TeamName=teams)
          playerPointsRanks = get_nhl_points_leaders(session=session, TeamName=teams)
          goalSavePercentageRanks = get_nhl_goaltending_save_percentage_leaders(session=session, TeamName=teams)
          return templates.TemplateResponse(request=request, name="nhlstats_leaders.html",
                                            context={"playerGoalRanks": playerGoalRanks,
                                                     "playerPlusMinusRanks": playerPlusMinusRanks,
                                                     "playerPointsRanks": playerPointsRanks,
                                                     "goalSavePercentageRanks": goalSavePercentageRanks})



def get_nhl_teams(session: SessionDep)-> list[nhl_teams]:
    sqlStmt = text("select id, name as team_name from teams order by name")

    results = session.execute(sqlStmt)
    rows = results.mappings().all()
    teamList = [teams(**row) for row in rows]

    return teamList
def get_nhl_goal_leaders(session: SessionDep, TeamName:int=0)-> list[nhl_goal_leaders]:
          print(f"Getting NHL Goal Leaders for Team: {TeamName}")
          if(TeamName != 0):
                query = text("""
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
                """)
                results = session.execute(query, {"TeamName": TeamName})
                rows = results.mappings().all()
                playerGoalRanks = [nhl_goal_leaders(**row) for row in rows]
          else:
                query = text("""
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
                """)
                results = session.execute(query)
                rows = results.mappings().all()
                playerGoalRanks = [nhl_goal_leaders(**row) for row in rows]

          return playerGoalRanks
def get_nhl_plusminus_leaders(session: SessionDep, TeamName:int=0)-> list[nhl_goal_leaders]:

          if(TeamName != 0):
                query = text("""
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
                """)
                results = session.execute(query, {"TeamName": TeamName})
                rows = results.mappings().all()
                plusminusGoalRanks = [nhl_plusminus_leaders(**row) for row in rows]
          else:
                query = text("""
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
                """)
                results = session.execute(query)
                rows = results.mappings().all()
                plusminusGoalRanks = [nhl_plusminus_leaders(**row) for row in rows]

          return plusminusGoalRanks

def get_nhl_points_leaders(session: SessionDep, TeamName:int=0)-> list[nhl_points_leaders]:

          if(TeamName != 0):
                query = text("""
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
                """)
                results = session.execute(query, {"TeamName": TeamName})
                rows = results.mappings().all()
                pointsGoalRanks = [nhl_points_leaders(**row) for row in rows]
          else:
                query = text("""
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
                """)
                results = session.execute(query, {"TeamName": TeamName})
                rows = results.mappings().all()
                pointsGoalRanks = [nhl_points_leaders(**row) for row in rows]

          return pointsGoalRanks
def get_nhl_goaltending_save_percentage_leaders(session: SessionDep, TeamName:int=0)-> list[nhl_goaltending_save_percentage_leaders]:

          if(TeamName != 0):
                query = text("""
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
                """)
                results = session.execute(query, {"TeamName": TeamName})
                rows = results.mappings().all()
                savePercentageRanks = [nhl_goaltending_save_percentage_leaders(**row) for row in rows]
          else:
                query = text("""
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
                """)
                results = session.execute(query, {"TeamName": TeamName})
                rows = results.mappings().all()
                savePercentageRanks = [nhl_goaltending_save_percentage_leaders(**row) for row in rows]

          return savePercentageRanks

@app.get("/items/{item_id}")
def read_item(item_id: int, q:str | None = None):
    return {"item_id": item_id, "q": q}

@app.get("/appname")
async def get_app_name():
    return {"app_name": "Hockey Playoff API"}
