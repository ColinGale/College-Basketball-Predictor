from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
import time

years = ["2018", "2019", "2022", "2023", "2025"]
all_years = []
for year in years:
    kenpom_url = 'https://kenpom.com/index.php?y=' + year
    data = Request(kenpom_url, headers={"User-Agent": "Mozilla/5.0"})
    webpage = urlopen(data).read()
    webpage_str = str(webpage, "utf-8")

    kenpom_stats_table = pd.read_html(StringIO(webpage_str))[0]
    # Drop the columns to one level only
    for index in range(len(kenpom_stats_table.columns[0]) - 1):
        kenpom_stats_table.columns = kenpom_stats_table.columns.droplevel()

    kenpom_stats_table["Year"] = year
    team_names = kenpom_stats_table["Team"].str.split(" ", expand=False)

    # Remove the seed at the end of the team name
    for row in team_names.to_list():
        if isinstance(row, list):
            if len(row) > 1:
                spot = None
                for index in range(len(row)):
                    if row[index].isnumeric():
                        spot = index
                    if row[index] == "St." and index != 0:
                        row[index] = "State"

                big_row = team_names.to_list().index(row)
                if spot:
                    team_names[big_row] = " ".join(row[:spot])
                else:
                    team_names[big_row] = " ".join(row)
            else:
                big_row = team_names.to_list().index(row)
                team_names[big_row] = row[0]

    kenpom_stats_table["Team"] = team_names

    # Rename ranking columns to be removed
    for num in [6, 8, 10, 12]:
        kenpom_stats_table.columns.values[num] = kenpom_stats_table.columns[num] + "_ranking"

    drop_columns = ["ORtg.1", "DRtg.1", "NetRtg.1", "ORtg_ranking", "DRtg_ranking", "Luck_ranking", "AdjT_ranking"]
    kenpom_stats_table = kenpom_stats_table.drop(drop_columns, axis=1)

    # Rename opponent columns
    for num2 in range(9, 12):
        kenpom_stats_table.columns.values[num2] = "SOS_" + kenpom_stats_table.columns[num2]
    kenpom_stats_table.columns.values[12] = "NCSOS_" + kenpom_stats_table.columns[12]

    # Remove + from columns' data
    for col in ["NetRtg", "Luck", "SOS_NetRtg", "NCSOS_NetRtg"]:
        kenpom_stats_table[col] = kenpom_stats_table[col].str.replace("+", "")

    kenpom_stats_table[["W", "L"]] = kenpom_stats_table["W-L"].str.split("-", expand=True)

    kenpom_stats_table = kenpom_stats_table.dropna()
    kenpom_stats_table.drop(columns="W-L", inplace=True)
    kenpom_stats_table = kenpom_stats_table[kenpom_stats_table["Rk"] != "Rk"]
    all_years.append(kenpom_stats_table)

kenpom_total = pd.concat(all_years)







