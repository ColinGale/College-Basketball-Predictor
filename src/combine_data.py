import pandas as pd
from missing_dict import MissingDict
from kenpom_data import all_years as all_years_ken
import string


# From sports-reference to kenpom
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
        "Southern Mississippi": "Southern Miss",
        "St. John's (NY)": "St. John's",
        "Kansas City": "UMKC",
        r"Texasâ\x80\x93Rio Grande Valley": "UT Rio Grande Valley",
        "Loyola (MD)": "Loyola MD",
        "Southern California": "USC",
        r"Illinoisâ\x80\x93Chicago": "Illinois Chicago",
        "Brigham Young": "BYU",
        r"Arkansasâ\x80\x93Pine Bluff": "Arkansas Pine Bluff",
        "IPFW": "Purdue Fort Wayne",
        "UT Martin": "Tennessee Martin",
        "Omaha": "Nebraska Omaha",
        "St. Mary's (CA)": "Saint Mary's",
        "Mount St. Mary's": "Mount State Mary's",
        "Pennsylvania": "Penn",
        "Louisiana State": "LSU",
        "Central Connecticut State": "Central Connecticut",
        "Saint Francis (PA)": "St. Francis PA",
        r"Texas A&Mâ\x80\x93Corpus Christi": "Texas A&M Corpus Chris",
        r"Louisianaâ\x80\x93Monroe": "Louisiana Monroe",
        'Albany (NY)': "Albany",
        "St. Francis Brooklyn": "St. Francis NY",
        "Queens (NC)": "Queens",
        r"Texas A&Mâ\x80\x93Commerce": "Texas A&M Commerce"

    }

def weight_stats(new_df):
    for stat in ["fg_pct", "efg_pct", "fg3_pct", "tov"]:
        new_df[stat] = new_df[stat] * new_df["last_5_avg_net"]

    return new_df


def get_average_net(new_df, index, kenpom, year):
    if isinstance(new_df.iloc[index]["opp_name_abbr"], list):
        last_5_opponents = new_df.iloc[index]["opp_name_abbr"]
    else:
        last_5_opponents = new_df.iloc[index]["opp_name_abbr"].strip("[]").split(",")
    net_rtg_list = []
    for name in last_5_opponents:
        name = name.strip().strip("''").strip('""')
        if name in map_values:
            name = map_values[name]

        if name == "Detroit Mercy" and year == "2019":
            name = "Detroit"

        try:
            net_rtg_list.append(float(kenpom[kenpom["Team"] == name]["NetRtg"].iloc[0]))
        except IndexError as e:
            net_rtg_list.append(None)

    total_rtg = 0
    total_games = 5
    for num in net_rtg_list:
        if num == None:
            total_games -= 1
        else:
            total_rtg += num

    average = total_rtg / total_games

    return average


def combined_data():
    combined = []
    years = ["2018", "2019", "2022", "2023"]

    for year in years:
        index1 = years.index(year)
        kenpom = all_years_ken[index1]
        new_df = pd.read_csv(f"team_stats_{year}.csv")

        new_df["pt_diff"] = new_df["pt_diff"] / 5

        averages = []
        for index, row in new_df.iterrows():
            average = get_average_net(new_df, index, kenpom, year)
            averages.append(average)

        new_df["last_5_avg_net"] = averages
        new_df["adjusted_pt_diff"] = new_df["pt_diff"] * new_df["last_5_avg_net"]

        new_df = weight_stats(new_df)

        combined.append(new_df)

    return combined


