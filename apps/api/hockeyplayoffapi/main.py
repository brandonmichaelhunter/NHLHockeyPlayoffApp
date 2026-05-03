from typing import Annotated, Union
from fastapi import Depends, FastAPI, HTTPException, Query, Request,Header
from sqlmodel import Field, Session, SQLModel, create_engine, select
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
import os
from pathlib import Path
from api.hockeyplayoffapi.models.nhl_scores import nhl_scores
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
      return {"status": "ready"}
@app.get("/nhl_scores", response_class=HTMLResponse)
async def read_nhl_scores(session: SessionDep, request: Request,  hx_request: Annotated[Union[str, None], Header()] = None, nhlScoreDateSelect:str=None):
    sqlStmt = select(nhl_scores).where(nhl_scores.date == nhlScoreDateSelect)
    nhlScores = session.exec(sqlStmt).all()
    
    if hx_request:
       resp = templates.TemplateResponse(request=request, name="nhlscores.html", context={"nhlScores": nhlScores})
       return resp
    return JSONResponse(content=jsonable_encoder(nhlScores))

@app.get("/", response_class=HTMLResponse)
async def index(request:Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/items/{item_id}")
def read_item(item_id: int, q:str | None = None):
    return {"item_id": item_id, "q": q}

@app.get("/appname")
async def get_app_name():
    return {"app_name": "Hockey Playoff API"}

