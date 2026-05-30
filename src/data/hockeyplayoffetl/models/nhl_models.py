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

class DynamicObject:
      def __init__(self, **kwargs):
          for key, value in kwargs.items():
              setattr(self, key, value)
