from flask import Flask, render_template, redirect, url_for, request, abort
from riotwatcher import LolWatcher, RiotWatcher, ApiError
import os
from dotenv import load_dotenv
from markupsafe import escape
import LolMatch
from summoner import Summoner

# Load API key and other secrets from .env file
load_dotenv()

app = Flask(__name__)

# Create an instance of Riot and LoL watcher to pass around
riot_api = RiotWatcher(api_key=os.getenv("RIOT_API_KEY"))
league_api = LolWatcher(api_key=os.getenv("RIOT_API_KEY"))


# Render the homepage upon entering the site
@app.route('/', methods=['GET', 'POST'])
def show_homepage():
    return render_template('homepage.html')


# Base url, used to collect the parameters from url submission
@app.route('/user/', methods=['GET'])
def user_form_handle():
    if request.args:
        # Gather all required parameters. The escape is to avoid any attempts at HTML injection
        summoner = str(escape(request.args.get('summoner_name')))
        tagline = str(escape(request.args.get('tagline')))
        region = str(escape(request.args.get('region')))
        # After collecting all of it, we redirect into the next part with the summoner, tagline, and region
        return redirect(url_for('user_search', summoner_name=summoner, tagline=tagline, region=region))
    else:
        # If they didn't type in anything, redirect them back into homepage
        return redirect(url_for('show_homepage'))


# Brings up user stats using their in-game name, tagline, and region
@app.route('/user/<region>/<summoner_name>-<tagline>', methods=['GET'])
def user_search(summoner_name, tagline, region):

    # Try to query the Riot API for their player information
    try:
        player = Summoner.from_game_name(lol_watcher=league_api, riot_watcher=riot_api, game_name=summoner_name,
                                         tag_line=tagline, region=region)
        player_info = player.get_summoner_info()
    # Improve the error handling here
    # Handle API errors raised from RiotWatcher
    # Our own custom one as well
    except Exception as e:
        abort(404, 'Summoner could not be found. Please try again.')

    # Collect all the info we collected to pass it to the player stats template
    html_payload = {
        'summoner_name': summoner_name,
        'tagline': tagline,
        'region': region,
        'summoner_level': player_info['summonerLevel'],
        'player_icon': player_info['profileIconId']
    }

    # Render the player stats and pass in the payload
    return render_template('player_stats_template.html', html_payload=html_payload)


# Handles any 404 error raised
@app.errorhandler(404)
def page_404(error):
    # Renders the error template and passes the error message to display
    return render_template('error_page.html', error_msg=error)
