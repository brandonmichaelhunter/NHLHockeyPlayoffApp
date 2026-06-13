from typing import Union
from turtle import home
from dataclasses import dataclass
#from dns.edns import option_from_wire_parser


@dataclass
class player:
    id: int
    first_name: str
    m_inital:str
    last_name:str
    age:int
    birth_date:str
    headshot_url:str

@dataclass
class gameboxscore:
    id:int
    gameID:int
    period:int
    awayScore:int
    homeScore:int


@dataclass
class playergamestats:
    id:int
    gameID:int
    gameTypeID:int
    playerID:int
    position:str
    goals:int
    assists:int
    points:int
    plusMinus:int
    pim:int
    hits:int
    powerPlayGoals:int
    faceoffWinningPctg:int
    blockedShots:int
    shifts:int
    evenStrengthShotsAgainst:str
    powerPlayShotsAgainst:str
    shorthandedShotsAgainst:str
    saveShotsAgainst:str
    savePctg:int
    evenStrengthGoalsAgainst:int
    powerPlayGoalsAgainst:int
    shorthandedGoalsAgainst:int
    goalsAgainst:int
    shotsAgainst:int
    saves:int
    toi:str

@dataclass
class game:
    id:int
    gameDate:str
    gameNumber:int
    gameScheduleStateId:int
    gameStateId:int
    gameTypeId:int
    homeScore:int
    homeTeamId:int
    period:int
    seasonId:int
    visitingScore:int
    visitingTeamId:int
    year:int
    month:int
    day:int

@dataclass
class season:
    id:int
    startYear:int
    endYear:int

@dataclass
class teamroster:
    id:int
    teamID:int
    playerID:int
    startDate:str
    endDate:str
    jerseyNumber:str
    position:str

@dataclass
class nhl_team:
    id:int
    franchise_id:int
    name:str
    abbrv:str
    logoURL:str
    city:str
    state:str
    country:str

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

@dataclass
class nhl_game_score:
    game_date: str=""
    home_team:str=""
    home_team_image:str=""
    away_team:str=""
    away_team_image:str=""
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

@dataclass
class nhl_playoff_schedule:
      gameID:int=0
      seasonID:int=0
      gameDate:str=""
      gameStartTime:str=""
      homeTeamID:int=0
      homeScore:int=0
      awayTeamID:int=0
      awayScore:int=0
      topSeedsWin:str=""
      topSeedsTeamID:int=0
      bottomSeedsWin:str=""
      bottomSeedsTeamID:int=0
      seriesTitle:str=""
      round:str=""
      stationInfo:str=""
      gameNumberOfSeries:int=0
      winningGoaliePlayerID:int=0
      winningGoalScorerPlayerID:int=0
      venueName:str=""
      periods:int=0
      seriesInfo:str=""



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

@dataclass
class nhl_score:
    team_name:str = ""
    active:bool = True

@dataclass
class api_url_request:
      function_name:str = ""
      endpoint_url:str = ""

@dataclass
class api_url_response:
      function_name:str = ""
      json_response:Union[dict, None] = None
@dataclass
class data_request:
    dbCursor:object=None
    dbConn:object=None
    debug:bool=False
    jsonData:object=None
    entityData:object=None
    label:str=""

@dataclass
class nhl_goaltending_gaa_leader:
    rank:int=0
    first_name:str=""
    last_name:str=""
    team_name:str=""
    gaa:float=0.0
    headshot_url:str=""
    teamlogo_url:str=""

@dataclass
class nhl_goaltending_save_pct_leader:
    rank:int=0
    first_name:str=""
    last_name:str=""
    team_name:str=""
    save_percentage:float=0.0
    headshot_url:str=""
    teamlogo_url:str=""

@dataclass
class nhl_score:
    game_date: str=""
    home_team:str=""
    home_team_image:str=""
    away_team:str=""
    away_team_image:str=""
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

@dataclass
class nhl_skate_goal_leader:
    rank:int=0
    first_name:str=""
    last_name:str=""
    team_name:str=""
    goals:float=0.0
    headshot_url:str=""
    teamlogo_url:str=""

@dataclass
class nhl_skate_leader:
    rank:int=0
    first_name:str=""
    last_name:str=""
    team_name:str=""
    points:int=0
    headshot_url:str=""
    teamlogo_url:str=""

@dataclass
class nhl_score:
    team_name:str = ""
    active:bool = True


class DynamicObject:
      def __init__(self, **kwargs):
          for key, value in kwargs.items():
              setattr(self, key, value)
