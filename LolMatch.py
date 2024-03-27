from riotwatcher import LolWatcher
import pandas as pd


def get_match_details(lol_watcher: LolWatcher, match_id: str, region: str) -> dict:
    """
    :param lol_watcher: LolWatcher instance to query for match details
    :param match_id: Match ID of game
    :param region: Region/server of player/match
    :return: A dictionary with all details of the match
    """
    return lol_watcher.match.by_id(match_id=match_id, region=region)


def get_match_stats(match: dict) -> pd.DataFrame:
    """
    Returns the stats of each player in the match
    :param match: dictionary/JSON of the entire match
    :return: dataframe of player stats
    """
    df = pd.DataFrame.from_dict(match["info"]["participants"])
    df.set_index(keys=["riotIdGameName", "riotIdTagline", "puuid"], inplace=True)
    return df


def get_match_info(match: dict) -> pd.DataFrame:
    """
    Returns information about the match like map, duration, timestamps, etc.
    :return: data from of general match details
    """
    df = pd.DataFrame.from_dict(match["info"])
    df.drop(columns=["participants"])
    return df
