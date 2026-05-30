from dataclasses import dataclass

@dataclass
class nhl_goaltending_save_pct_leader:
    rank:int=0
    first_name:str=""
    last_name:str=""
    team_name:str=""
    save_percentage:float=0.0
    headshot_url:str=""
    teamlogo_url:str=""