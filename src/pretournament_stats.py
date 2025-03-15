import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
from tournament_data import all_years
from kenpom_data import kenpom_total
from missing_dict import MissingDict
import re


def calculate_ema(data, alpha):
    ema = data[0]  # Start with first game's value
    for stat in data[1:]:
        ema = alpha * stat + (1 - alpha) * ema
    return ema



# Team names that don't match up between the two sites
map_values = {
        "Loyola (IL)": "Loyola Chicago",
        "NC State": "N.C. State",
        "Miami (FL)": "Miami FL",
        "UNC": "North Carolina",
        "Ole Miss": "Mississippi",
        "Gardener-Webb": "Gardener Webb",
        "FDU": "Fairleigh Dickinson",
        "UC-Irvine": "UC Irvine",
        "UConn": "Connecticut",
        "St. Peter's": "Saint Peter's",
        "Pitt": "Pittsburgh",
        "College of Charleston": "Charleston",
        "Texas A&M-Corpus Christi": "Texas A&M Corpus Chris",
        "UCSB": "UC Santa Barbra",
    }

reversed_map_values = {value: key for key, value in map_values.items()}

team_url = {
        "penn": "pennsylvania",
        "nc-state": "north-carolina-state",
        "tcu": "texas-christian",
        "umbc": "maryland-baltimore-county",
        "unc": "north-carolina",
        "unc-greensboro": "north-carolina-greensboro",
        "ucf": "central-florida",
        "vcu": "virginia-commonwealth",
        "lsu": "louisiana-state",
        "uc-irvine": "california-irvine",
        "saint-marys": "saint-marys-ca",
        "ole-miss": "mississippi",
        "fdu": "fairleigh-dickinson",
        "st-peters": "saint-peters",
        "usc": "southern-california",
        "uab": "alabama-birmingham",
        "uconn": "connecticut",
        "louisiana": "louisiana-lafayette",
        "unc-asheville": "north-carolina-asheville",
        "pitt": "pittsburgh",
        "ucsb": "california-santa-barbara",
        "uc-san-diego": "california-san-diego"
    }

years = ["2018", "2019", "2022", "2023"]

def get_team_stats():
    all_years_merged = []
    for index1 in range(len(all_years)):
        all_teams = all_years[index1]["Team"].to_list()  # keep the original names
        all_teams = list(dict.fromkeys(all_teams))  # removes duplicates and keeps the order

        year = years[index1]
        stat_df = pd.DataFrame(columns=["Team", "team_game_result", "fg_pct", "fg3_pct", "ft_pct", "efg_pct", "fga", "fg3a", "fta", "orb", "drb", "tov","opp_name_abbr", "pt_diff"])

        for index2 in range(len(all_teams)):
            team = all_teams[index2]
            if team in reversed_map_values:
                team = reversed_map_values[team]
            print(team)
            stat_df = team_stats(team, year, index2, stat_df)
            time.sleep(3.01)

        mapping = MissingDict(**map_values)
        stat_df["Team"] = stat_df["Team"].replace(mapping)
        tournament_games = pd.merge(all_years[index1], stat_df, on="Team", how="inner")

        # Change team names to better match kenpom site
        tournament_games["Team"] = tournament_games["Team"].replace(mapping)
        tournament_games["Opponent"] = tournament_games["Opponent"].replace(mapping)

        tournament_games.to_csv(f"team_stats_{year}.csv")

def name_to_url(name):
    name = re.sub(r"[ .&()']", "", name.lower().replace(" ", "-"))
    if name in team_url.keys():
        name = team_url[name]

    return name


def team_stats(team, year, index, stat_df):
    # Formats the team name into url
    team_url = name_to_url(team)
    tournament_url = f"https://www.sports-reference.com/cbb/schools/{team_url}/men/{year}-gamelogs.html"

    data = requests.get(tournament_url)
    soup = BeautifulSoup(data.text, features="html.parser")

    team_log = soup.find("table")
    games = team_log.find_all("tr", {"id": True})

    stop_point = 0
    for row in range(len(games)):
        stop_point += 1
        game_type = games[row].find("td", {"data-stat": "game_type"}).text
        if game_type == "ROUND-64":
            stop_point = row
            break

    games = games[stop_point - 5:stop_point]  # get the last 5 games before tourney

    stat_dict = {"team_game_result": 0, "efg_pct": 0, "fga": 0, "fg_pct": 0, "fg3a": 0, "fg3_pct": 0, "fta": 0,
                 "ft_pct": 0, "orb": 0, "drb": 0, "tov": 0, "opp_name_abbr": [], "pt_diff": 0}

    for key in stat_dict.keys():
        if key == "team_game_result":
            for game in games:
                stat = game.find("td", {"data-stat": f"{key}"})
                stat_data = int(stat.text == 'W')
                stat_dict[key] += stat_data
        elif key == "opp_name_abbr":
            for game in games:
                team_a = game.find("td", {"data-stat": f"{key}"})
                team1 = team_a.find("a").text
                stat_dict[key].append(team1)
        elif key == "pt_diff":
            score_diff_list = []
            for game in games:
                score1 = int(game.find("td", {"data-stat": "team_game_score"}).text)
                score2 = int(game.find("td", {"data-stat": "opp_team_game_score"}).text)
                score_diff_list.append(score1 - score2)
            stat_dict[key] = calculate_ema(score_diff_list, alpha=0.2)
        else:
            last_N_games = [float(game.find("td", {"data-stat": f"{key}"}).text) for game in games]
            stat_dict[key] = calculate_ema(last_N_games, alpha=0.2)

    total_averages = team_log.find_all("tr")[-1]
    num_games = 5
    for key in stat_dict.keys():
        if key == "team_game_result":
            stat = total_averages.find("td", {"data-stat": f"{key}"})
            num_games = int(stat.text.split("-")[0]) + int(stat.text.split("-")[1])
        elif key == "opp_name_abbr":
            pass
        elif key == "pt_diff":
            stat_dict[key] = stat_dict[key] / 5
        else:
            stat = total_averages.find("td", {"data-stat": f"{key}"})
            stat_data = float(stat.text)
            stat_dict[key] = stat_dict[key] / stat_data
            if "pct" not in key:
                stat_dict[key] *= num_games

    stat_df.loc[index] = [team, *stat_dict.values()]

    return stat_df

def kenpom_to_sports_ref(name):
    if name in reversed_map_values:
        name = reversed_map_values[name]
    return name

def kenpom_to_sports_ref_df(df):
    # Change team names to better match kenpom site
    mapping = MissingDict(**reversed_map_values)
    df["Team"] = df["Team"].replace(mapping)
    try:
        df["Opponent"] = df["Opponent"].replace(mapping)
    except KeyError as e:
        pass

    return df


def sports_ref_to_kenpom(df):
    # Change team names to better match kenpom site
    mapping = MissingDict(**map_values)
    df["Team"] = df["Team"].replace(mapping)
    try:
        df["Opponent"] = df["Opponent"].replace(mapping)
    except KeyError as e:
        pass
    return df

