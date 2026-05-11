from sqlmodel import Field, Session, SQLModel, create_engine, select
class nhl_scores(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    date: str = Field(index=True)
    home_team:str
    home_team_image:str
    away_team:str
    away_team_image:str
    home_score:int=0
    away_score:int=0
    first_period_home_score:int=0
    second_period_home_score:int=0
    third_period_home_score:int=0
    overtime_home_score:int=0
    final_home_score:int=0
    first_period_away_score:int=0
    second_period_away_score:int=0
    third_period_away_score:int=0
    overtime_away_score:int=0
    final_away_score:int=0
    round:str=""
    game_number:int=0
    series_info:str=""
