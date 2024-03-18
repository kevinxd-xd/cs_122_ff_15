from riotwatcher import RiotWatcher, LolWatcher
import os
from dotenv import load_dotenv

# Load API key and other secrets from .env file
load_dotenv()


class LoLPlayer:
    # For getting riot player, there's only 4 regions: Americas, Asia, Europe, ESPORTS
    # For getting league players: BR1, EUN1, EUW1, JP1, KR, LA1, LA2, NA1, OC1, PH2, RU, SG2, TH2, TR1, TW2, VN2
    # Possible Solution: Have a constant of mapped for each region and how they correspond to the riot regions?
    # ex. "BR1": "Americas", etc.
    def __init__(self, game_name: str, tag_line: str, region: str):
        """
        Creates an instance of the Player class. Allows us to pass game name, tag line and region parameters to create
        the riot watcher and LoL watcher.
        :param game_name: Name of the player's Riot account
        :param tag_line: The tag line of the player's Riot account ex. #NA1
        :param region: The region of the player's Riot account
        :return: None
        """
        riot_watcher = RiotWatcher(os.getenv('RIOT_API_KEY'))
        riot_player = riot_watcher.account.by_riot_id(game_name=game_name, tag_line=tag_line, region=region)
        self.__lol_watcher = LolWatcher(os.getenv('RIOT_API_KEY'))
        self.__player_puuid = riot_player["puuid"]
        self.__summoner_info = self.__lol_watcher.summoner.by_puuid(encrypted_puuid=self.__player_puuid, region="NA1")

    def get_player_puuid(self):
        return self.__player_puuid

    def get_player_puuid(self):
        return self.__player_puuid

    def get_summoner_info(self):
        return self.__summoner_info

    def print_player_info(self):
        """
        Prints basic info about the player in League of Legends
        :return: None
        """
        print(f"Summoner Name: {self.get_summoner_info()["name"]}\nLevel: {self.get_summoner_info()["summonerLevel"]}\n")


