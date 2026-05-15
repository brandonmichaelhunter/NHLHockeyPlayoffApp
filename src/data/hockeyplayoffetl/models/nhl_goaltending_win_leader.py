from dataclasses import dataclass

@dataclass
class nhl_goaltending_win_leader:
    rank:int=0
    first_name:str=""
    last_name:str=""
    team_name:str=""
    wins:int=0
    headshot_url:str=""
    teamlogo_url:str=""