import json
import os
from flask import Flask, render_template, redirect, url_for, request, abort, send_from_directory
from werkzeug import security
from riotwatcher import LolWatcher, RiotWatcher, ApiError
from dotenv import load_dotenv
from markupsafe import escape
from summoner import Summoner
import constants
from GraphGeneration import CustomError
import GraphGeneration

# Load API key and other secrets from .env file
load_dotenv(override=True)

app = Flask(__name__)

# Config for serving JSON files safely
app.config['DATA'] = os.path.join(app.root_path, "data")

# Graphs to generate
app.config['GRAPHS'] = [GraphGeneration.create_duration_graph,
                        GraphGeneration.graphs_gamemodes_dist,
                        GraphGeneration.graphs_surrender_dist,
                        GraphGeneration.skillshots_v_abilities,
                        GraphGeneration.position_played]

# Create an instance of Riot and LoL watcher to pass around
riot_api = RiotWatcher(api_key=os.getenv("RIOT_API_KEY"))
league_api = LolWatcher(api_key=os.getenv("RIOT_API_KEY"))


# Render the homepage upon entering the site
@app.route('/', methods=['GET'])
def show_homepage():
    return render_template('homepage.html', regions=constants.regions)


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
    except ApiError as err:
        # Convert error response to a dictionary that we can access
        err_dct = json.loads(err.response.text)
        status_code = err_dct['status']['status_code']
        status_message = err_dct['status']['message']
        return render_template("error_page.html", status_code=status_code, status_message=status_message)
    except CustomError as e:
        return render_template("error_page.html", status_code=403, status_message=e.args[0])
    except:
        abort(404, 'Something went wrong. Please try again')

    match_ids = player.get_match_ids()  # list of most recent 20 match ids

    # Collect all the info we collected to pass it to the player stats template

    # Path to where the data is saved
    player.export_json(
        matches=match_ids, data_directory=app.config['DATA'], league_api=league_api)
    json_file_path = os.path.join(
        app.config['DATA'], player.puuid(), "summoner.json")

    player_data = GraphGeneration.load_file(json_file_path)
    graphs = GraphGeneration.create_graphs(player_data, app.config['GRAPHS'])
    html_payload = {
        'summoner_name': summoner_name,
        'tagline': tagline,
        'region': region,
        'summoner_level': player_info['summonerLevel'],
        'player_icon': player_info['profileIconId'],
        'puuid': player_info['puuid'],
        'graphs': graphs,
    }

    # Render the player stats and pass in the payload
    return render_template('player_stats_template.html', html_payload=html_payload)


@ app.route('/json_submission', methods=['POST'])
def json_submission():
    submission_data = request.files['json_upload']
    # If the file type is not of JSON type then we render an error page
    if submission_data.mimetype != 'application/json':
        return render_template("error_page.html", status_code=400, status_message="Not a JSON file!")

    # Data is ready to be used
    player_data = json.load(submission_data)
    try:
        graphs = GraphGeneration.create_graphs(
            player_data, app.config["GRAPHS"])
    except CustomError as e:
        return render_template("error_page.html", status_code=400, status_message=e.args[0])

    html_payload = {
        'summoner_name': player_data['summonerInfo']['summoner_name'],
        'tagline': player_data['summonerInfo']['tagline'],
        'region': player_data['summonerInfo']['region'],
        'summoner_level': player_data['summonerInfo']['summonerLevel'],
        'player_icon': player_data['summonerInfo']['profileIconId'],
        'graphs': graphs,
    }
    # Render the player stats and pass in the payload
    return render_template('player_stats_template.html', html_payload=html_payload)

# How to send a file from directory to user
# Source: https://stackoverflow.com/questions/24577349/flask-download-a-file


@ app.route('/download/<puuid>', methods=['GET'])
def download(puuid):
    file_path = security.safe_join(app.config['DATA'], puuid)
    if os.path.exists(file_path):
        return send_from_directory(directory=app.config['DATA'], path=security.safe_join(puuid, "summoner.json"))
    else:
        return render_template('error_page.html', status_code=404, status_message="File not found")


@ app.errorhandler(404)
def page_404(error):
    # Renders the error template and passes the error message to display
    return render_template('error_page.html', status_code=404, status_message=error)
