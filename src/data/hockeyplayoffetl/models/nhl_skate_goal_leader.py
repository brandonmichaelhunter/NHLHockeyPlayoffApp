from dataclasses import dataclass

@dataclass
class nhl_skate_goal_leader:
    rank:int=0
    first_name:str=""
    last_name:str=""
    team_name:str=""
    goals:float=0.0
    headshot_url:str=""
    teamlogo_url:str=""
