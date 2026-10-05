from sqlmodel import SQLModel


class nhl_playoff_schedule(SQLModel, table=False):
    gamedate: str = ""
    gamestarttime: str = ""
    awayteamname: str = ""
    awayscore: int = 0
    awayteamnameabbrv: str = ""
    awayteamlogourl: str = ""
    hometeamname: str = ""
    homescore: int = 0
    hometeamnameabbrv: str = ""
    hometeamlogourl: str = ""
    seriestitle: str = ""
    playoffround: str = ""
    tvstation: str = ""
    hometeamvenuename: str = ""
    winninggoalieplayerid: int = 0
    goaliefirstname: str = ""
    goalielastname: str = ""
    goalieheadshoturl: str = ""
    winninggoalscorerplayerid: int = 0
    skaterfirstname: str = ""
    skaterlastname: str = ""
    skaterheadshoturl: str = ""
    seriesinfo: str = ""
