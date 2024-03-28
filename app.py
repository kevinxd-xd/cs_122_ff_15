from flask import Flask, render_template, request
from riotwatcher import LolWatcher, RiotWatcher, ApiError
import os
from dotenv import load_dotenv
import LolMatch
from summoner import Summoner

# Load API key and other secrets from .env file
load_dotenv()

app = Flask(__name__)

# Create an instance of Riot and LoL watcher to pass around
riot_api = RiotWatcher(api_key=os.getenv("RIOT_API_KEY"))
league_api = LolWatcher(api_key=os.getenv("RIOT_API_KEY"))


@app.route('/', methods=['GET', 'POST'])
def hello_world():
    if request.method == 'POST':
        summoner_name = request.form['summoner_name']
        tagline = request.form['tagline']
        region = request.form['region']
        player = Summoner.from_game_name(lol_watcher=league_api, riot_watcher=riot_api, game_name=summoner_name, tag_line=tagline, region=region)
        player_info = player.get_summoner_info()

        html_payload = {
            'summoner_name': summoner_name,
            'tagline': tagline,
            'region': region,
            'summoner_level': player_info['summonerLevel'],
            'player_icon': player_info['profileIconId']
        }

        return render_template('player_stats_template.html', html_payload=html_payload)
    else:
        return render_template('homepage.html')
