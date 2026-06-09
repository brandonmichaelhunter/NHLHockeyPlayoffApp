from sqlmodel import Field, Session, SQLModel, create_engine, select
class nhl_goal_leaders(SQLModel, table=False):
    player_id: int
    total_goals: int
    league_ranking: int
    player_firstname:str
    player_lastname:str
    player_headshot:str
    player_position:str
    team_name: str
    team_abbrv: str
    team_logo: str

class nhl_plusminus_leaders(SQLModel, table=False):
    player_id: int
    plus_minus: int
    league_ranking: int
    player_firstname:str
    player_lastname:str
    player_headshot:str
    player_position:str
    team_name: str
    team_abbrv: str
    team_logo: str

class nhl_points_leaders(SQLModel, table=False):
    player_id: int
    total_points: int
    league_ranking: int
    player_firstname:str
    player_lastname:str
    player_headshot:str
    player_position:str
    team_name: str
    team_abbrv: str
    team_logo: str

class nhl_goaltending_save_percentage_leaders(SQLModel, table=False):
    player_id: int
    save_percentage: float
    league_ranking: int
    player_firstname:str
    player_lastname:str
    player_headshot:str
    player_position:str
    team_name: str
    team_abbrv: str
    team_logo: str

class nhl_goaltending_gaa_leaders(SQLModel, table=False):
    player_id: int
    gaa: float
    league_ranking: int
    player_firstname:str
    player_lastname:str
    player_headshot:str
    player_position:str
    team_name: str
    team_abbrv: str
    team_logo: str

class nhl_goaltending_wins_leaders(SQLModel, table=False):
    player_id: int
    wins: int
    league_ranking: int
    player_firstname:str
    player_lastname:str
    player_headshot:str
    player_position:str
    team_name: str
    team_abbrv: str
    team_logo: str

class nhl_playoff_game_schedules(SQLModel, table=False):
       game_id:int
       game_date:str
       home_team:str
       home_team_image:str
       away_team:str
       away_team_image:str
       home_score:int
       away_score:int
       first_period_home_score:int
       second_period_home_score:int
       third_period_home_score:int
       overtime_home_score:int
       final_home_score:int
       first_period_away_score:int
       second_period_away_score:int
       third_period_away_score:int
       overtime_away_score:int
       final_away_score:int
       round:str=""
       game_number:int=0
