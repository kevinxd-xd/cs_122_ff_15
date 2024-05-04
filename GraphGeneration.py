from datetime import datetime, timedelta
import json
import pandas as pd
import plotly.express as px


class CustomError(Exception):
    ''' Custom Exception for error handling'''
    pass


def load_file(file_path: str) -> dict:
    """
    Loads player's JSON file from the data folder
    :param file_path: The file path of the JSON file
    :return: A dictionary containing player information
    """
    with open(file_path, 'r', encoding='UTF-8') as fo:
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
        try:
            create_graph = func(player_data)
            graphs.append(create_graph)
        except KeyError as e:
            raise CustomError(400, "Invalid JSON file") from e
    return graphs


def create_duration_graph(player_data: dict) -> str:
    '''
    Creates a box plot with the durations of the games played 
    :param player_data: A dictionary from a JSON file containing player information
    :returns: A string of the graph's HTML
    '''
    # Scatter Plot: Past 20 Game Duration
    try:
        match_ids = list(player_data.keys())[1:]
    except KeyError as e:
        raise CustomError(400, "Invalid JSON file content") from e

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
    '''
    Creates a pie chart of the different gamemodes played
    :param player_data: A dictionary from a JSON file containing player information
    :returns: A string of the graph's HTML
    '''
    game_modes = []
    game_modes_count = {}
    match_ids = list(player_data.keys())[1:]

    for match_id in match_ids:
        try:
            game_mode = player_data[match_id]['info']['gameMode']
            if game_mode == 'CHERRY':
                game_mode = 'ARENA'
            game_modes.append(game_mode)
        except KeyError as e:
            raise CustomError(400, "Invalid JSON file content") from e

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
    '''
    Creates a pie chart of the game end result
    :param player_data: A dictionary from a JSON file containing player information
    :returns: A string of the graph's HTML
    '''
    match_ids = list(player_data.keys())[1:]
    # Set up counts
    result_counts = {
        "win": 0,
        "gameEndedInSurrender": 0,
        "gameEndedInEarlySurrender": 0,
        "loss": 0
    }

    for match_id in match_ids:
        try:
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
        except KeyError:
            print(f"No end result information for Game ID: {match_id}")

    win_loss_data = pd.DataFrame({'Results': result_counts.keys(),
                                  'Count': result_counts.values()})

    pie_graph = px.pie(data_frame=win_loss_data, values='Count', names="Results",
                       title="Win/Surrender/Loss Distribution",
                       color_discrete_sequence=[
                           "green", "purple", "blue", "red"],
                       category_orders={
                           "Results": ["win", "gameEndedInSurrender", "gameEndedInEarlySurrender", "loss"]})
    graph_html = pie_graph.to_html(full_html=False)

    return graph_html


def skillshots_v_abilities(player_data: dict) -> str:
    '''
    Creates a scatter plot of the skillshots and abilities used
    :param player_data: A dictionary from a JSON file containing player information
    :returns: A string of the graph's HTML
    '''
    try:
        match_ids = list(player_data.keys())[1:]
    except KeyError as e:
        raise CustomError(400, "Invalid JSON file content") from e

    skillshots_hit = []
    abilities_used = []
    game_modes = []
    for match_id in match_ids:
        try:
            match_info_pd = pd.Series(player_data[match_id])

            skillshots_hit.append(
                match_info_pd['info']['participants']['challenges']['skillshotsHit']
            )
            abilities_used.append(
                match_info_pd['info']['participants']['challenges']['abilityUses'])

            game_mode = player_data[match_id]['info']['gameMode']
            if game_mode == 'CHERRY':
                game_mode = 'ARENA'
            game_modes.append(game_mode)
        except KeyError:
            print(
                f"No skillshots and abilities information available for Game ID: {match_id}")

    abilities_used_df = pd.DataFrame(
        data={'skillshots hit': skillshots_hit,
              'abilities used': abilities_used,
              'game mode': game_modes}
    )

    graph = px.scatter(
        data_frame=abilities_used_df,
        x='skillshots hit',
        y='abilities used',
        color='game mode',
        title="Skillshots Landed Compared to Total Abilities Used"
    )

    graph_html = graph.to_html(full_html=False)

    return graph_html


def position_played(player_data: dict) -> str:
    '''
    Creates a pie chart showing the distribution of the roles played
    :param player_data: A dictionary from a JSON file containing player information
    :returns: A string of the graph's HTML
    '''
    try:
        match_ids = list(player_data.keys())[1:]
    except KeyError as e:
        raise CustomError(400, "Invalid JSON file content") from e

    positions_count = {
        "TOP": 0,
        "JUNGLE": 0,
        "MIDDLE": 0,
        "BOTTOM": 0,
        "SUPPORT": 0,
        "NO ROLE": 0
    }

    for match_id in match_ids:
        try:
            match_info_pd = pd.Series(player_data[match_id])
            role = match_info_pd['info']['participants']['lane']
            if role == 'TOP':
                positions_count[role] += 1
            elif role == 'JUNGLE':
                positions_count[role] += 1
            elif role == 'MIDDLE':
                positions_count[role] += 1
            elif role == 'BOTTOM':
                positions_count[role] += 1
            elif role == 'SUPPORT':
                positions_count[role] += 1
            else:
                positions_count['NO ROLE'] += 1
        except KeyError:
            print(f"No role information for Game ID: {match_id}")

    positions_data = pd.DataFrame(
        {'Lane Position': positions_count.keys(),
         'Count': positions_count.values()}
    )

    pie_graph = px.pie(
        data_frame=positions_data,
        values='Count',
        names='Lane Position',
        title='Lane Position Distribution',
        color_discrete_sequence=["orange", "red",
                                 "green", "blue",
                                 "purple", "black"],
        category_orders={"Lane Position":
                         ["TOP", "JUNGLE", "MIDDLE",
                          "BOTTOM", "SUPPORT", "NO ROLE"]}
    )

    graph_html = pie_graph.to_html(full_html=False)

    return graph_html
