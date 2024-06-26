from riotwatcher import LolWatcher, ApiError
import pandas as pd
from GraphGeneration import CustomError


def get_match_details(lol_watcher: LolWatcher, match_id: str, region: str) -> dict:
    """
    Retrieves the specified match from the League API and returns a dictionary
    :param lol_watcher: LolWatcher instance to query for match details
    :param match_id: Match ID of game
    :param region: Region/server of player/match
    :return: A dictionary with all details of the match
    """
    try:
        return lol_watcher.match.by_id(match_id=match_id, region=region)
    except ApiError as e:
        raise CustomError(400, e.args[0]) from e
    except Exception as e:
        raise CustomError(400, "Unknown Error. Check logs for more information.") from e


def get_player_stats(match: dict) -> pd.DataFrame:
    """
    Returns the stats of each player in the match
    :param match: dictionary/JSON of the entire match
    :return: dataframe of player stats
    """
    df = pd.DataFrame.from_dict(match["info"]["participants"])
    df.set_index(keys=["puuid"], inplace=True)
    return df


def get_match_info(match: dict) -> pd.Series:
    """
    Returns information about the match like map, duration, timestamps, etc.
    :return: Series with general match details
    """
    df = pd.Series(match["info"])
    df.drop(labels=["participants"], inplace=True)
    return df
