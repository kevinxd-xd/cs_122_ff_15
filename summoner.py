import os
import json
from riotwatcher import RiotWatcher, LolWatcher, ApiError
import constants
import LolMatch
from GraphGeneration import CustomError


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
        try:
            summoner = riot_watcher.account.by_puuid(
                puuid=puuid, region="americas")
        except ApiError as e:
            # Exception chaining
            # Source: https://stackoverflow.com/questions/696047/re-raise-exception-with-a-different-type-and-message-preserving-existing-inform
            raise CustomError(403, "Invalid API key") from e
        except Exception as e:
            raise CustomError(400, "Unknown Error. Check logs for more information.") from e
        else:
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
        try:
            summoner = riot_watcher.account.by_riot_id(
                game_name=game_name, tag_line=tag_line, region="americas")
        except ApiError as e:
            # Convert error response to a dictionary that we can access
            err_dct = json.loads(e.response.text)
            if err_dct['status']['status_code'] == 403:
                # Exception chaining
                # Source: https://stackoverflow.com/questions/696047/re-raise-exception-with-a-different-type-and-message-preserving-existing-inform
                raise CustomError(403, "Invalid API key") from e
            else:
                raise CustomError(400, err_dct['status']['message']) from e
        except Exception as e:
            raise CustomError(400, "Unknown Error. Check logs for more information.") from e
        else:
            return cls(lol_watcher=lol_watcher, puuid=summoner['puuid'], game_name=game_name, tag_line=tag_line,
                       region=region)

    def get_summoner_info(self) -> dict:
        """
        Returns summoner name, profile icon, level, PUUID, etc.
        :return: basic information about the summoner
        """
        try:
            return self.__lol_watcher.summoner.by_puuid(encrypted_puuid=self.__summoner_puuid, region=self.__region)
        except ApiError as e:
            raise CustomError(400, e.args[0]) from e
        except Exception as e:
            raise CustomError(400, "Unknown Error. Check logs for more information.") from e

    def get_match_ids(self) -> list[str]:
        """
        Returns a list of match ids of recent games played by summoner (Default: 20)
        :return: list of match_ids
        """
        try:
            return self.__lol_watcher.match.matchlist_by_puuid(puuid=self.__summoner_puuid, region=self.__region)
        except ApiError as e:
            raise CustomError(400, e.args[0]) from e
        except Exception as e:
            raise CustomError(400, "Unknown Error. Check logs for more information.") from e

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

    def export_json(self, matches: list, data_directory: str, league_api: LolWatcher):
        """
        Creates a JSON representation of the summoner's account
        :param data_directory: directory of where all player data is stored
        :param matches: list of recent 20 match ids
        :param league_api: str of the RIOT API key
        """
        json_file = {}  # dictionary to convert to json file. Key is match_id. Value is participant match info

        # adds summoner info to json file
        json_file['summonerInfo'] = self.get_summoner_info()
        json_file['summonerInfo']['summoner_name'] = self.summoner_name()
        json_file['summonerInfo']['tagline'] = self.tag_line()
        json_file['summonerInfo']['region'] = self.region()

        for match in matches:
            try:
                json_file[match] = LolMatch.get_match_details(
                    lol_watcher=league_api, match_id=match, region=self.region())  # dict

                for i, participant in enumerate(json_file[match]['metadata']['participants']):
                    # Finds the index of summoner to filter for summoner's match information
                    if participant == self.puuid():
                        index = i

                summoner_match_info = json_file[match]['info']['participants'][index]
                json_file[match]['info']['participants'] = summoner_match_info
            except ApiError:
                # Game information is not available. Move on to the next match id
                print(f"Game Info for {match} cannot be found")

        user_directory = os.path.join(data_directory, self.puuid())
        if not os.path.exists(user_directory):
            os.makedirs(user_directory)
        with open(os.path.join(user_directory, 'summoner.json'), 'w', encoding='UTF-8') as fo:
            json.dump(json_file, fo)  # converts dict to json
