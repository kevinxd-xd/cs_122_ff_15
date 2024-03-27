from riotwatcher import LolWatcher, RiotWatcher, ApiError
import os
from dotenv import load_dotenv
import LolMatch as lm
from summoner import Summoner

# Load API key and other secrets from .env file
load_dotenv()

# Create an instance of Riot and LoL watcher to pass around
riot_api = RiotWatcher(api_key=os.getenv("RIOT_API_KEY"))
league_api = LolWatcher(api_key=os.getenv("RIOT_API_KEY"))

# Player types in this username
# We create a summoner object
player = Summoner.from_game_name(riot_watcher=riot_api, lol_watcher=league_api, game_name="Hide on bush",
                                 tag_line="KR1",
                                 region="Korea")

# We the player's most recent match
match_id = player.get_match_ids()[0]
# Get the match details
match_details = lm.get_match_details(lol_watcher=league_api, match_id=match_id, region=player.region())
# Get the match stats of each player
player_stats = lm.get_match_stats(match_details)
# Let's get all the outcomes of the match
print(player_stats.loc[:, ['win']])
