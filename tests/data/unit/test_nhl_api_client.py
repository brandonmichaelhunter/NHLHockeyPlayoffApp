import pytest
from unittest.mock import MagicMock, patch
from src.data.hockeyplayoffetl.services.nhl_api_client import nhl_api_client


@pytest.fixture
def client():
    base_url = "https://fake-api.nhle.com/v1"
    return nhl_api_client(base_url=base_url)


@pytest.mark.unit
def test_get_teams_info_success(mocker, client):
    # mock data.
    expected_data = {"data": [{"teamName": "Team A"}, {"teamName": "Team B"}]}
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = expected_data
    mock_get = mocker.patch('requests.get', return_value=mock_response)
    
    # Act
    result = client.get_teams_info()
    
    # Assert
    mock_get.assert_called_once_with(f"{client.baseUrl}/stats/rest/en/team")
    assert result == expected_data


@pytest.mark.unit    
def test_get_team_roster_success(mocker, client):
    param_team_abbrv = "PHL"
    expected_data = {"data": [{"first_name": "John", "last_name": "Doe"}, {"first_name": "Jane", "last_name": "Smith"}]}
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = expected_data
    mock_get = mocker.patch('requests.get', return_value=mock_response)

    # Act
    result = client.get_team_roster(param_team_abbrv)

    # Assert
    mock_get.assert_called_once_with(f"{client.baseUrl}/v1/roster/{param_team_abbrv}/current")
    assert result == expected_data

@pytest.mark.unit    
def test_get_player_info_success(mocker, client):
    player_id = "8000"
    expected_data = {"data": [{"id": "8000", "first_name": "John", "last_name": "Doe"}, {"id": "8001", "first_name": "Jane", "last_name": "Smith"}]}
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = expected_data
    mock_get = mocker.patch('requests.get', return_value=mock_response)

    # Act
    result = client.get_player_info(player_id)

    # Assert
    mock_get.assert_called_once_with(f"{client.baseUrl}/v1/player/{player_id}/landing")
    assert result == expected_data

@pytest.mark.unit    
def test_get_game_boxscore_success(mocker, client):
    player="88888"
    season="1111"
    game_type="2"
    expected_data = {
                    "seasonId":1111, 
                    "gameTypeId":2,
                    "playerStatsSeason":[
                    {"season": 20252026, "gameTypes": [2, 3]}, 
                    {"season": 20242025, "gameTypes": [2, 3]}],
                    "gameLog":[
                        {
                            "gameId": 2023021306,"teamAbbrev": "EDM",
                            "homeRoadFlag": "R","gameDate": "2024-04-17","goals": 0,"assists": 0,
                            "commonName": { "default": "Oilers" },
                            "opponentCommonName": { "default": "Coyotes" },
                            "points": 0,"plusMinus": -2,"powerPlayGoals": 0,
                            "powerPlayPoints": 0,"gameWinningGoals": 0,"otGoals": 0,"shots": 2,"shifts": 19,
                            "shorthandedGoals": 0,"shorthandedPoints": 0,"pim": 0,"opponentAbbrev": "ARI","toi": "18:10"
                        },
                        {
                            "gameId": 2023021293,"teamAbbrev": "EDM","homeRoadFlag": "H",
                            "gameDate": "2024-04-15","goals": 1,"assists": 1,
                            "commonName": { "default": "Oilers" },
                            "opponentCommonName": {"default": "Sharks"},
                            "points": 2,"plusMinus": 3,
                            "powerPlayGoals": 0,"powerPlayPoints": 0,"gameWinningGoals": 0,
                            "otGoals": 0,"shots": 3,"shifts": 16,"shorthandedGoals": 0,
                            "shorthandedPoints": 0,"pim": 0,"opponentAbbrev": "SJS","toi": "15:45"
                        }
                    ]
    }
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = expected_data
    mock_get = mocker.patch('requests.get', return_value=mock_response)

    # Act
    result = client.get_game_boxscore(player, season, game_type)

    # Assert
    mock_get.assert_called_once_with(f"{client.baseUrl}/v1/player/{player}/game-log/{season}/{game_type}")
    assert result == expected_data
    
@pytest.mark.unit    
def test_get_seasons_success(mocker, client):
    
    expected_data = [1111,2222,3333,4444]
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = expected_data
    mock_get = mocker.patch('requests.get', return_value=mock_response)

    # Act
    result = client.get_seasons()

    # Assert
    mock_get.assert_called_once_with(f"{client.baseUrl}/v1/season")
    assert result == expected_data
    
@pytest.mark.unit    
def test_game_boxscore_by_game_id(mocker, client):
    
    expected_data = [1111,2222,3333,4444]
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = expected_data
    mock_get = mocker.patch('requests.get', return_value=mock_response)

    # Act
    game_id = "2023021306"
    result = client.get_game_boxscore_by_game_id(game_id)

    # Assert
    mock_get.assert_called_once_with(f"{client.baseUrl}/v1/gamecenter/{game_id}/boxscore")
    assert result == expected_data