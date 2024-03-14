import random

import cassiopeia as cass
import os
from dotenv import load_dotenv

load_dotenv()

cass.set_riot_api_key(os.getenv("RIOT_API_KEY"))

summoner = cass.get_summoner(name="Hide on bush", region="KR")

print("{name} is a level {level} summoner on the {region} server.".format(name=summoner.name,
                                                                          level=summoner.level,
                                                                          region=summoner.region))

