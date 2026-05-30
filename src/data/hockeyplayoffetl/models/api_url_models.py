from dataclasses import dataclass

@dataclass
class api_url_request:
      function_name:str = ""
      endpoint_url:str = ""

@dataclass
class api_url_response:
      function_name:str = ""
      json_response:dict = None
