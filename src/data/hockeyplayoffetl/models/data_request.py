
from dataclasses import dataclass

@dataclass
class data_request:
    dbCursor:object=None
    dbConn:object=None
    debug:bool=False
    jsonData:object=None
    entityData:object=None
    label:str=""
