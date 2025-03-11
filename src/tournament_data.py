import requests
from bs4 import BeautifulSoup
import pandas as pd
from src.missing_dict import MissingDict

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
        "UCSB": "UC Santa Barbra"
    }

years = ["2018", "2019", "2022", "2023"]
all_years = []
for year in years:
    tournament_url = f'https://www.sports-reference.com/cbb/postseason/men/{year}-ncaa.html'
    data = requests.get(tournament_url)
    soup = BeautifulSoup(data.text, features="html.parser")

    # Gets the bracket
    bracket_div = soup.find("div", {"id": "brackets"})
    # Gets all regions
    all_regions_divs = bracket_div.find_all("div", {"id": ["east", "midwest", "south", "west", "national"]})
    # Initializes df
    tournament_games = pd.DataFrame(columns=["Seed", "Team", "Opponent", "Team Score", "Opponent Score", "Result"])

    all_regions = []
    for region in all_regions_divs:
        rounds = region.find_all("div", {"class": "round"})
        all_rounds = []
        for r in range(len(rounds[:-1])):
            round = rounds[r]
            # New df for each round
            round_games = pd.DataFrame(columns=["Seed","Region", "Team", "Opponent", "Team Score", "Opponent Score", "Result"])
            winners = round.find_all("div", {"class": "winner"})
            seeds = [w.find("span").text for w in winners]
            winners = [w.find_all("a") for w in winners]

            # Stores the winners name, their score, and their seed
            winners = [[winners[index][0].text, winners[index][1].text, seeds[index]] for index in range(len(winners))]

            game = round.find_all("div")

            losers = [g.find("div", {"class": None}) for g in game if g.find("div") is not None]
            seeds = [int(l.find("span").text) for l in losers]
            losers = [l.find_all("a") for l in losers]

            # Stores the losers name, their score, and their seed
            losers = [[losers[index][0].text, losers[index][1].text, seeds[index]] for index in range(len(losers))]

            round_num = r if region["id"] != "national" else r + 4

            # Formats important data
            round_games["Year"] = [year for w in winners] + [year for l in losers]
            round_games["Region"] = [region["id"] for w in winners] + [region["id"] for l in losers]
            round_games["Round"] = [round_num + 1 for w in winners] + [round_num + 1 for l in losers]
            round_games["Team"] = [w[0] for w in winners] + [l[0] for l in losers]
            round_games["Seed"] = [w[2] for w in winners] + [l[2] for l in losers]
            round_games["Opponent"] = [l[0] for l in losers] + [w[0] for w in winners]
            round_games["Team Score"] = [w[1] for w in winners] + [l[1] for l in losers]
            round_games["Opponent Score"] = [l[1] for l in losers] + [w[1] for w in winners]
            round_games["Result"] = [num < len(round_games) // 2 for num in range(len(round_games))]
            round_games["Result"] = round_games["Result"].astype(int)
            all_rounds.append(round_games)

        region_games = pd.concat(all_rounds)
        region_games.reset_index(drop=True, inplace=True)

        all_regions.append(region_games)

    tournament_games = pd.concat(all_regions)
    tournament_games.reset_index(drop=True, inplace=True)

    # Change team names to better match kenpom site
    mapping = MissingDict(**map_values)
    tournament_games["Team"] = tournament_games["Team"].replace(mapping)
    tournament_games["Opponent"] = tournament_games["Opponent"].replace(mapping)

    all_years.append(tournament_games)



