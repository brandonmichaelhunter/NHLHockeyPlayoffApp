from dataclasses import dataclass

@dataclass
class nhl_goaltending_win_leader:
    player_id:int=0
    team_id:int=0
    seasons:str=""
    first_name:str=""
    last_name:str=""
    team_name:str=""
    team_abbrv:str=""
    wins:int=0
    headshot_url:str=""
    teamlogo_url:str=""
