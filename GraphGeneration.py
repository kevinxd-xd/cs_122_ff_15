from datetime import datetime
import time
import json
import pandas as pd
import plotly.express as px


def load_file(file_path: str) -> dict:
    """
    Loads player's JSON file from the data folder
    :param file_path: The file path of the JSON file
    :return: A dictionary containing player information
    """
    with open(file_path, 'r') as fo:
        player_data = json.load(fo)
    return player_data


def create_graphs(player_data, graph_funcs) -> list:
    """Returns a list of graphs to be displayed
    :param player_data: A dictionary from a JSON file containing player information
    :returns: A list of html graphs
    """
    graphs = []
    for func in graph_funcs:
        create_graph = func(player_data)
        graphs.append(create_graph)
    return graphs


def create_duration_graph(player_data: dict) -> str:
    # Scatter Plot: Past 20 Game Duration

    # Extract game times
    graphs = []
    match_ids = list(player_data.keys())[1:]
    '''Scatter Plot: Past 20 Game Duration'''
    # Extract game times
    date = []
    durations = []
    for match_id in match_ids:
        match_info_pd = pd.Series(player_data[match_id])

        date.append(match_info_pd['info']['gameCreation'])

        hr_min_sec = time.strftime("%H:%M:%S", time.gmtime(
            match_info_pd['info']['gameDuration']))
        durations.append(hr_min_sec)

    dd_df = pd.DataFrame(data={'date': date, 'duration': durations})
    # Convert all unix times to dates
    # Timestamp error
    # Source: https://stackoverflow.com/questions/37494983/python-fromtimestamp-oserror
    dd_df['date'] = dd_df['date'].apply(
        lambda ts: datetime.fromtimestamp(ts / 1000))

    graph = px.scatter(data_frame=dd_df, x="date",
                       y="duration", title="Duration of Past 20 Games")
    graph_html = graph.to_html(full_html=False)

    return graph_html


def graphs_gamemodes_dist(player_data: dict) -> str:
    game_modes = []
    game_modes_count = {}
    match_ids = list(player_data.keys())[1:]

    for match_id in match_ids:
        game_modes.append(player_data[match_id]['info']['gameMode'])

    for mode in game_modes:
        if mode in game_modes_count:
            game_modes_count[mode] += 1
        else:
            game_modes_count[mode] = 1

    game_mode_df = pd.DataFrame({'Game Mode': game_modes_count.keys(),
                                 'Count': game_modes_count.values()})
    pie_graph = px.pie(data_frame=game_mode_df, values='Count', names="Game Mode",
                       title="Game Mode Distribution")
    graph_html = pie_graph.to_html(full_html=False)

    return graph_html

