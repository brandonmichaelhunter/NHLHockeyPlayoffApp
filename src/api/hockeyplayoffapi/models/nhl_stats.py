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
 