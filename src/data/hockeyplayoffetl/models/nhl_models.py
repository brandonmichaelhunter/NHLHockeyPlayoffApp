from dataclasses import dataclass

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
      game_date:str=""
      start_time:str=""
      year:int=0
      month:int=0
      day:int=0
      homeTeamID:int=0
      awayTeamID:int=0
      homeTeamScore:int=0
      awayTeamScore:int=0
      seriesInfo:str=""
      topSeedsWin:str=""
      bottomSeedsWin:str=""
      round:str=""
      seriesTitle:str=""
class DynamicObject:
      def __init__(self, **kwargs):
          for key, value in kwargs.items():
              setattr(self, key, value)
