import random

from riotwatcher import LolWatcher, RiotWatcher, ApiError
import os
from dotenv import load_dotenv

# Load API key and other secrets from .env file
load_dotenv()

# Get the account associated with: game_name, tag_line, and region of player
# This let's use get the user's PUUID which will let us make requests based on the new endpoints instead of
# the deprecated one
riot_acc = RiotWatcher(api_key=os.getenv("RIOT_API_KEY"))
player_riot = riot_acc.account.by_riot_id(game_name="Hide on bush", tag_line="KR1", region="asia")



# Create instance to access LoL endpoints
lol_watcher = LolWatcher(api_key=os.getenv("RIOT_API_KEY"))

summoner = lol_watcher.summoner.by_puuid(encrypted_puuid=player_riot["puuid"], region="KR")

print("{name} is a level {level} summoner on the {region} server.".format(name=summoner["name"],
                                                                          level=summoner["summonerLevel"],
                                                                          region="korea"))



