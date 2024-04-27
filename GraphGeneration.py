from datetime import datetime, time, timedelta
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
    """
    Returns a list of graphs to be displayed
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

    graphs = []
    match_ids = list(player_data.keys())[1:]
    # Extract game times
    date = []
    durations = []
    for match_id in match_ids:
        match_info_pd = pd.Series(player_data[match_id])

        date.append(match_info_pd['info']['gameCreation'])

        hr_min_sec = timedelta(seconds=match_info_pd['info']['gameDuration'])
        durations.append(hr_min_sec)

    dd_df = pd.DataFrame(data={'date': date, 'duration': durations})
    # Convert all unix times to dates
    # Timestamp error
    # Source: https://stackoverflow.com/questions/37494983/python-fromtimestamp-oserror
    dd_df['date'] = dd_df['date'].apply(
        lambda ts: datetime.fromtimestamp(ts / 1000).date())

    # How to fix timedelta formatting issue, plotly doesn't support timedelta, workaround listed in Github issue
    # Source 1: https://community.plotly.com/t/timeseries-plot-with-timedelta-axis/23560
    # Source 2: https://github.com/plotly/plotly.py/issues/801
    dd_df['duration'] = dd_df['duration'] + pd.to_datetime('1970/01/01')

    graph = px.box(data_frame=dd_df, x="date",
                       y="duration", title="Duration of Past 20 Games")
    # Force format to ignore the workaround added
    graph.update_yaxes(tickformat="%H:%M:%S")
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


def graphs_surrender_dist(player_data: dict) -> str:
    match_ids = list(player_data.keys())[1:]
    # Set up counts
    result_counts = {
        "win": 0,
        "gameEndedInSurrender": 0,
        "gameEndedInEarlySurrender": 0,
        "loss": 0
    }

    for match_id in match_ids:
        win = player_data[match_id]['info']['participants']['win']
        surrender = player_data[match_id]['info']['participants']['gameEndedInSurrender']
        surrender_early = player_data[match_id]['info']['participants']['gameEndedInEarlySurrender']

        if win:
            result_counts['win'] += 1
        elif surrender and not surrender_early:
            result_counts['gameEndedInSurrender'] += 1
        elif not surrender and not surrender_early:
            result_counts['loss'] += 1
        else:
            result_counts['gameEndedInEarlySurrender'] += 1

    win_loss_data = pd.DataFrame({'Results': result_counts.keys(),
                                  'Count': result_counts.values()})

    pie_graph = px.pie(data_frame=win_loss_data, values='Count', names="Results",
                       title="Win/Surrender/Loss Distribution",
                       color_discrete_sequence=["green", "purple", "blue", "red"],
                       category_orders={
                           "Results": ["win", "gameEndedInSurrender", "gameEndedInEarlySurrender", "loss"]})
    graph_html = pie_graph.to_html(full_html=False)

    return graph_html

def win_loss_ratio(player_data: dict) -> str:
    # player_data['info']['participants']['win'] # boolean
    pass


def abilities_used(player_data: dict) -> str:
    # player_data['info'][participants']['challenges']['abilityUses']  # int
    pass


def longest_time_alive(player_data: dict) -> str:
    # player_data['info'][participants']['longestTimeSpentLiving'] # int (seconds)
    pass


def skillshots_hit_v_abilities(player_data: dict) -> str:
    # player_data['info'][participants']['challenges']['abilityUses']
    # player_data['info'][participants']['challenges']['skillshotsDodged']
    pass