from riotwatcher import RiotWatcher, LolWatcher
import constants
import json


class Summoner:

    # Type hinting and default values
    # Source: https://stackoverflow.com/questions/38727520/how-do-i-add-default-parameters-to-functions-when-using-type-hinting
    def __init__(self, lol_watcher: LolWatcher, puuid: str, game_name: str, tag_line: str, region: str):
        """
        Creates an instance of the summoner class.
        :param lol_watcher: LolWatcher instance to perform queries
        :param game_name: Name of the summoner's Riot account
        :param tag_line: The tag line of the summoner's Riot account ex. #NA1
        :param region: The region of the summoner's Riot account
        :param puuid: The puuid of the summoner's Riot account
        :return: None
        """
        # If PUUID is passed in as a parameter, we can set the fields
        self.__lol_watcher = lol_watcher
        self.__summoner_puuid = puuid
        self.__game_name = game_name
        self.__tag_line = tag_line
        # Temporary workaround for sometimes input is, for example, "KR", but "KR" does not map anywhere, will fix when frontend is up
        self.__region = constants.regions[region] if region in constants.regions else region

    # Idea to use class method to create two possible types of the same class
    # We can create a player class using either the PUUID or the game name + tag line of a player
    # Source: ChatGPT
    @classmethod
    def from_puuid(cls, lol_watcher: LolWatcher, riot_watcher: RiotWatcher, puuid: str, region: str):
        """
        Creates an instance of the summoner with the given puuid and region
        :param lol_watcher: LolWatcher instance to perform queries
        :param riot_watcher: RiotWatcher instance to perform queries
        :param puuid: PUUID of the summoner
        :param region: Region/server of the summoner
        :return: Summoner object
        """
        summoner = riot_watcher.account.by_puuid(
            puuid=puuid, region="americas")
        return cls(lol_watcher=lol_watcher, puuid=puuid, game_name=summoner['gameName'], tag_line=summoner['tagLine'],
                   region=region)

    @classmethod
    def from_game_name(cls, lol_watcher: LolWatcher, riot_watcher: RiotWatcher, game_name: str, tag_line: str,
                       region: str):
        """
        Creates an instance of the summoner class using the given game name and tag line and region
        :param lol_watcher: LolWatcher instance to perform queries
        :param riot_watcher: RiotWatcher instance to perform queries
        :param game_name: In game name of the summoner
        :param tag_line: The tag line of the summoner
        :param region: Region/server of the summoner
        :return: Summoner object
        """
        summoner = riot_watcher.account.by_riot_id(
            game_name=game_name, tag_line=tag_line, region="americas")
        return cls(lol_watcher=lol_watcher, puuid=summoner['puuid'], game_name=game_name, tag_line=tag_line,
                   region=region)

    def get_summoner_info(self) -> dict:
        """
        Returns summoner name, profile icon, level, PUUID, etc.
        :return: basic information about the summoner
        """
        return self.__lol_watcher.summoner.by_puuid(encrypted_puuid=self.__summoner_puuid, region=self.__region)

    def get_match_ids(self) -> list[str]:
        """
        Returns a list of match ids of recent games played by summoner (Default: 20)
        :return: list of match_ids
        """
        return self.__lol_watcher.match.matchlist_by_puuid(puuid=self.__summoner_puuid, region=self.__region)

    def puuid(self) -> str:
        """
        Returns the summoner's PUUID
        :return: summoner's PUUID
        """
        return self.__summoner_puuid

    def summoner_name(self) -> str:
        """
        Returns the summoner's name
        :return: summoner's name
        """
        return self.__game_name

    def tag_line(self) -> str:
        """
        Returns the tag line of the summoner's account. Ex. NA1
        :return: tag line of summoner
        """
        return self.__tag_line

    def region(self) -> str:
        """
        Returns the region/server summoner's account is on
        :return: summoner's region
        """
        return self.__region

    def export_json(self) -> json:
        """
        Returns a JSON representation of the summoner's account
        :return: JSON file of basic summoner info
        """
        newdict = {}
        newdict.update(self.get_summoner_info())
        no_space = self.__game_name.replace(" ", "_")
        file_str = f"./data/{no_space}_summoner_info.json"
        with open(file_str, "w") as outfile:
            json.dump(newdict, outfile)
