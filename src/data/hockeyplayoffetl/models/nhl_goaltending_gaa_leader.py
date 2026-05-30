from dataclasses import dataclass

@dataclass
class nhl_goaltending_gaa_leader:
    rank:int=0
    first_name:str=""
    last_name:str=""
    team_name:str=""
    gaa:float=0.0
    headshot_url:str=""
    teamlogo_url:str=""