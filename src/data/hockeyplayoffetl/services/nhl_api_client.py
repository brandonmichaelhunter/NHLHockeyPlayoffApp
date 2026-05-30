import requests

class nhl_api_client:
    baseUrl: str = ""
    def __init__(self, base_url: str = "https://api-web.nhle.com"):
        self.baseUrl = base_url
    def fetch_nhl_data(self, endpoint:str):
        try:
            url = f"{self.baseUrl}/{endpoint}"
            #print(f"Fetching NHL API data from URL: {url}")
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Failed to fetch NHL API data. Status code: {response.status_code}")
        except Exception as e:
            raise Exception(f"An error occurred while fetching NHL API data: {e}")

    def fetch_nhl_data_with_url(self, url:str):
        try:
            #print(f"Fetching NHL API data from URL: {url}")
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                return None
                raise Exception(f"Failed to fetch NHL API data. Status code: {response.status_code}")
        except Exception as e:
            raise Exception(f"An error occurred while fetching NHL API data: {e}")
    def get_teams_info(self):
        try:
            url = f"{self.baseUrl}/stats/rest/en/team"
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Failed to fetch teams info. Status code: {response.status_code}")
        except Exception as e:
            raise Exception(f"An error occurred while fetching teams info: {e}")

    def get_team_roster(self, team_abbrv:str):
        try:
            url = f"{self.baseUrl}/v1/roster/{team_abbrv}/current"
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Failed to fetch team roster for {team_abbrv}. Status code: {response.status_code}")
        except Exception as e:
            raise Exception(f"An error occurred while fetching team roster for {team_abbrv}: {e}")

    def get_player_info(self, player_id:any):
        try:
            url = f"{self.baseUrl}/v1/player/{player_id}/landing"
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Failed to fetch player info for player ID {player_id}. Status code: {response.status_code}")
        except Exception as e:
            raise Exception(f"An error occurred while fetching player info for player ID {player_id}: {e}")

    def get_game_boxscore(self, player:any, season:any, game_type:any):

        try:
            url = f"{self.baseUrl}/v1/player/{player}/game-log/{season}/{game_type}"
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Failed to fetch game boxscore for player ID {player} in season {season} and game type {game_type}. Status code: {response.status_code}")
        except Exception as e:
            raise Exception(f"An error occurred while fetching game boxscore for player ID {player} in season {season} and game type {game_type}: {e}")

    def get_seasons(self):
        try:
            url = f"{self.baseUrl}/v1/season"
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Failed to fetch seasons. Status code: {response.status_code}")
        except Exception as e:
            raise Exception(f"An error occurred while fetching seasons: {e}")

    def get_game_info(self):
        try:
            url = f"{self.baseUrl}/stats/rest/en/game"
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Failed to fetch game info. Status code: {response.status_code}")
        except Exception as e:
            raise Exception(f"An error occurred while fetching game info: {e}")

    def get_game_boxscore_by_game_id(self, game_id:any):
        try:
            url = f"{self.baseUrl}/v1/gamecenter/{game_id}/boxscore"
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Failed to fetch game boxscore for game ID {game_id}. Status code: {response.status_code}")
        except Exception as e:
            raise Exception(f"An error occurred while fetching game boxscore for game ID {game_id}: {e}")
