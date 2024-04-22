import json
from datetime import datetime
import time
import os
import plotly.express as px
import pandas as pd

from flask import Flask, render_template, redirect, url_for, request, abort
from riotwatcher import LolWatcher, RiotWatcher, ApiError
from dotenv import load_dotenv
from markupsafe import escape
import LolMatch
from summoner import Summoner
import constants

# Load API key and other secrets from .env file
load_dotenv(override=True)

app = Flask(__name__)

# Create an instance of Riot and LoL watcher to pass around
riot_api = RiotWatcher(api_key=os.getenv("RIOT_API_KEY"))
league_api = LolWatcher(api_key=os.getenv("RIOT_API_KEY"))


# Render the homepage upon entering the site
@app.route('/', methods=['GET', 'POST'])
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
    except Exception as e:
        abort(404, 'Something went wrong. Please try again')

    graphs = []

    # Create graphs with Plotly here
    match_ids = player.get_match_ids()  # list of most recent 20 match ids

    '''Scatter Plot: Past 100 Game Duration'''
    # Extract game times
    date = []
    durations = []
    game_modes = []
    game_modes_count = {}
    for match_id in match_ids:
        match_details = LolMatch.get_match_details(
            lol_watcher=league_api, match_id=match_id, region=region)
        match_details_pd = LolMatch.get_player_stats(match=match_details)
        game_modes.append(match_details['info']['gameMode'])

        match_info_pd = LolMatch.get_match_info(match=match_details)

        date.append(match_info_pd['gameCreation'])

        hr_min_sec = time.strftime("%H:%M:%S", time.gmtime(
            match_info_pd['gameDuration']))
        durations.append(hr_min_sec)
    for mode in game_modes:
        if mode in game_modes_count:
            game_modes_count[mode] += 1
        else:
            game_modes_count[mode] = 1

    print(f"Game distributions: {game_modes_count}")
    dd_df = pd.DataFrame(data={'date': date, 'duration': durations})
    # Convert all unix times to dates
    # Timestamp error
    # Source: https://stackoverflow.com/questions/37494983/python-fromtimestamp-oserror
    dd_df['date'] = dd_df['date'].apply(
        lambda ts: datetime.fromtimestamp(ts / 1000))

    graph = px.scatter(data_frame=dd_df, x="date",
                       y="duration", title="Duration of Past 20 Games")
    graph_html = graph.to_html(full_html=False)
    graphs.append(graph_html)

    game_mode_df = pd.DataFrame({'Game Mode': game_modes_count.keys(),
                                 'Count': game_modes_count.values()})
    pie_graph = px.pie(data_frame=game_mode_df, values='Count', names="Game Mode",
                       title="Game Mode Distribution")
    graph_html = pie_graph.to_html(full_html=False)
    graphs.append(graph_html)

    # Collect all the info we collected to pass it to the player stats template

    # Path to where the data is saved
    # TODO: PATH URL EX) ./data/puuid/summoner.json
    Summoner.export_json(self=player, matches=match_ids,
                         league_api=league_api,
                         region=region)
    json_file_path = f"./data/{player.puuid()}/summoner.json"

    html_payload = {
        'summoner_name': summoner_name,
        'tagline': tagline,
        'region': region,
        'summoner_level': player_info['summonerLevel'],
        'player_icon': player_info['profileIconId'],
        'graphs': graphs,
        'json_file_path': json_file_path
    }

    # Render the player stats and pass in the payload
    return render_template('player_stats_template.html', html_payload=html_payload)


@app.route('/json_submission', methods=['POST'])
def json_submission():
    submission_data = request.files['json_upload']
    # If the file type is not of JSON type then we render an error page
    if submission_data.mimetype != 'application/json':
        return render_template("error_page.html", status_code=400, status_message="Not a JSON file!")

    # Data is ready to be used

    player_data = json.load(submission_data)

    graphs = []
    match_ids = list(player_data.keys())[1:]
    '''Scatter Plot: Past 100 Game Duration'''
    # Extract game times
    date = []
    durations = []
    game_modes = []
    game_modes_count = {}
    for match_id in match_ids:
        game_modes.append(player_data[match_id]['info']['gameMode'])
        match_info_pd = pd.Series(player_data[match_id])

        date.append(match_info_pd['info']['gameCreation'])

        hr_min_sec = time.strftime("%H:%M:%S", time.gmtime(
            match_info_pd['info']['gameDuration']))
        durations.append(hr_min_sec)
    for mode in game_modes:
        if mode in game_modes_count:
            game_modes_count[mode] += 1
        else:
            game_modes_count[mode] = 1

    dd_df = pd.DataFrame(data={'date': date, 'duration': durations})
    # Convert all unix times to dates
    # Timestamp error
    # Source: https://stackoverflow.com/questions/37494983/python-fromtimestamp-oserror
    dd_df['date'] = dd_df['date'].apply(
        lambda ts: datetime.fromtimestamp(ts / 1000))

    graph = px.scatter(data_frame=dd_df, x="date",
                       y="duration", title="Duration of Past 20 Games")
    graph_html = graph.to_html(full_html=False)
    graphs.append(graph_html)

    game_mode_df = pd.DataFrame({'Game Mode': game_modes_count.keys(),
                                 'Count': game_modes_count.values()})
    pie_graph = px.pie(data_frame=game_mode_df, values='Count', names="Game Mode",
                       title="Game Mode Distribution")
    graph_html = pie_graph.to_html(full_html=False)
    graphs.append(graph_html)

    puuid = player_data['summonerInfo']['puuid']
    json_file_path = f"./data/{puuid}/summoner.json"
    html_payload = {
        # TODO: PARSE THROUGH player_data TO LOAD INFO
        'summoner_name': player_data['summonerInfo']['summoner_name'],
        'tag_line': player_data['summonerInfo']['tagline'],
        'region': player_data['summonerInfo']['region'],
        'summoner_level': player_data['summonerInfo']['summonerLevel'],
        'player_icon': player_data['summonerInfo']['profileIconId'],
        'graphs': graphs,
        'json_file_path': json_file_path
    }
    # Render the player stats and pass in the payload
    return render_template('player_stats_template.html', html_payload=html_payload)

# Handles any 404 error raised


@ app.errorhandler(404)
def page_404(error):
    # Renders the error template and passes the error message to display
    return render_template('error_page.html', status_code=404, status_message="Page not found")
