from sqlmodel import Field, Session, SQLModel, create_engine, select
class nhl_teams(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    team_name: str = Field(index=True)
