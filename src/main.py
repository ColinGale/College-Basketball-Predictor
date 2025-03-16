import pandas as pd
import combine_data
import pretournament_stats
from src.kenpom_data import all_years as all_years_kenpom
from sklearn.ensemble import RandomForestClassifier


def main():
    # Get the team stats for all tournament teams, for each year
    all_years_tournament = combine_data.combined_data()

    # All predictive features that will be compared against an opponent's feature
    matchup_features = ["NetRtg", "ORtg", "DRtg", "AdjT", "Luck", "SOS_NetRtg", "SOS_ORtg", "SOS_DRtg", "NCSOS_NetRtg",
                        "W", "L", "Seed", "last_5_avg_net", "efg_pct", "pt_diff", "fg3_pct", "tov"]

    # Data to train and test the model
    merged = merge_all_data(all_years_kenpom[:-1], all_years_tournament, matchup_features)

    # Team statistics to make new predictions for user input
    kenpom_2025 = all_years_kenpom[-1]

    # Preparing team statistics from current year
    columns_to_int = ["Rk", "W", "L"]
    columns_to_float = ["NetRtg", "ORtg", "DRtg", "AdjT", "Luck", "SOS_NetRtg", "SOS_ORtg", "SOS_DRtg", "NCSOS_NetRtg"]
    kenpom_2025 = prepare_dataframe(kenpom_2025, columns_to_float, columns_to_int)

    # Data that the model uses to determine results
    predictors = ["NetRtg_diff", "ORtg_diff", "DRtg_diff",
                  "AdjT_diff", "Luck_diff", "SOS_NetRtg_diff", "SOS_ORtg_diff",
                  "SOS_DRtg_diff", "NCSOS_NetRtg_diff", "W_diff", "L_diff", "Seed_diff", "last_5_avg_net_diff",
                  "pt_diff_diff", "efg_pct_diff", "fg3_pct_diff", "tov_diff"]

    # Make predictions and get the accuracy and precision score
    rf = RandomForestClassifier(n_estimators=60, min_samples_split=25, random_state=1)
    accuracy, precision = make_predictions(merged, predictors, rf)
    print(f"This model's accuracy score: {accuracy}")
    print(f"This model's precision score: {precision}\n")

    # Show the actual versus predicted results for the tested predictions
    test = merged[merged["Year"] > 2022]
    preds = rf.predict(test[predictors])
    combined = pd.DataFrame(dict(actual=test["Result"], prediction=preds))
    print(pd.crosstab(index=combined["actual"], columns=combined["prediction"]))
    print()

    # Make predictions for the 2025 Tournament!
    while True:
        team1 = input("Enter a team: ")
        seed1 = int(input("Enter team's seed: "))
        team2 = input("Enter their opponent: ")
        seed2 = int(input("Enter opponent's seed: "))

        predictor = predict_matchup(team1, team2, kenpom_2025, seed1, seed2)

        # Handle invalid teams
        if predictor is not None:
            prediction = rf.predict(predictor[predictors])
            if prediction == 1:
                print(f"{team1} beats {team2}!\n")
            else:
                print(f"{team2} beats {team1}!\n")
        else:
            print(f"Invalid team names. Please try again.")

        end_loop = input("Continue Predicting? (y/n): ")
        if end_loop.lower() == "n" or end_loop.lower() == "no":
            break







def merge_all_data(all_years_kenpom, all_years_tournament, matchup_features):
    merged_list = []
    for year in range(len(all_years_kenpom)):
        merged = pd.merge(all_years_kenpom[year], all_years_tournament[year], on="Team", how="inner")
        merged.drop(["Year_x"], axis=1, inplace=True)
        merged.columns = merged.columns.str.replace("Year_y", "Year")

        columns_to_float = ["NetRtg", "ORtg", "DRtg", "AdjT", "Luck", "SOS_NetRtg", "SOS_ORtg", "SOS_DRtg", "NCSOS_NetRtg"]
        columns_to_int = ["Rk", "W", "L", "Seed", "Year", "Round", "Team Score", "Opponent Score"]

        merged = prepare_dataframe(merged, columns_to_float, columns_to_int)

        # Add a unique game identifier
        merged["Game ID"] = merged["Team"] + "-" + merged["Opponent"] + "-" + merged["Year"].astype(str)

        # Create opponent stats
        opponent_stats_columns = ["Team"] + matchup_features
        opponent_stats = merged[opponent_stats_columns].copy()

        # Rename the columns for the opponent stats
        for column in range(len(opponent_stats_columns)):
            if column != 0:
                opponent_stats.columns.values[column] = "Opp_" + opponent_stats.columns[column]
            else:
                opponent_stats.columns.values[column] = "Opponent"

        # Merge the opponent stats
        merged = pd.merge(merged, opponent_stats, on="Opponent", how="inner")

        # Matchup diff (helps with precision and accuracy being the same)
        for feature in matchup_features:
            merged[f"{feature}_diff"] = merged[feature] - merged[f"Opp_{feature}"]

        # Remove duplicates using Game ID
        merged.drop_duplicates(subset=["Game ID"], inplace=True)
        merged.drop(columns=["Game ID"], inplace=True)

        merged["NetRtg_diff"] = merged["NetRtg"] - merged["Opp_NetRtg"]
        merged = merged.sort_values(by=["Round", "Region", "Seed"])
        merged_list.append(merged)

    # Concatenate all years
    merged = pd.concat(merged_list, ignore_index=True)
    return merged



from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score

def make_predictions(merged, predictors, rf):
    train = merged[merged["Year"] <= 2022]  # train on data from tournaments before 2022
    test = merged[merged["Year"] > 2022]  # test on data from 2023 tournament
    rf.fit(train[predictors], train["Result"])
    preds = rf.predict(test[predictors])
    acc = accuracy_score(test["Result"], preds)
    precision = precision_score(test["Result"], preds)

    return acc, precision


def prepare_dataframe(df, columns_to_float, columns_to_int):
    # change respective columns to either a float or int for model
    for col in columns_to_float:
        try:
            df[col] = pd.to_numeric(df[col]).astype(float)
        except ValueError as e:
            print(f"Error converting column '{col}': {e}")
        except Exception as e:
            print(f"An unexpected error occurred while converting column '{col}': {e}")

    for col in columns_to_int:
        try:
            df[col] = pd.to_numeric(df[col]).astype(int)
        except ValueError as e:
            print(f"Error converting column '{col}': {e}")
        except Exception as e:
            print(f"An unexpected error occurred while converting column '{col}': {e}")

    # numerical values of conference and team for the model to handle
    df["Conf_code"] = df["Conf"].astype("category").cat.codes
    df["Team_code"] = df["Team"].astype("category").cat.codes

    return df



def predict_matchup(team1, team2, kenpom, seed1, seed2):
    # Get data for both teams
    team1_data = kenpom[kenpom["Team"] == team1].reset_index(drop=True)
    team2_data = kenpom[kenpom["Team"] == team2].reset_index(drop=True)

    # Handle team not found
    if team1_data.empty:
        print(f"Invalid Team: {team1}")
        if team2_data.empty:
            print(f"Invalid Team: {team2}")
        return None
    if team2_data.empty:
        print(f"Invalid Team: {team2}")
        return None

    team1_data, team2_data = add_statistics(team1, team1_data, team2, team2_data, kenpom)

    # Rename columns in team2_data to represent "Opponent"
    team2_data.columns = ["Opp_" + col if col != "Team" else "Opponent" for col in team2_data.columns]


    # Combine both teams into one DataFrame
    predictor = pd.concat([team1_data.reset_index(drop=True), team2_data.reset_index(drop=True)], axis=1)

    # Manually set Seed/Round to 1
    predictor["Seed"] = seed1
    predictor["Opp_Seed"] = seed2

    # Matchup diff and ratio (helps with precision and accuracy being the same)
    matchup_features = ["NetRtg", "ORtg", "DRtg", "AdjT", "Luck", "SOS_NetRtg", "SOS_ORtg", "SOS_DRtg", "NCSOS_NetRtg",
                        "W", "L", "Seed", "last_5_avg_net", "efg_pct", "pt_diff", "fg3_pct", "tov"]
    for feature in matchup_features:
        predictor[f"{feature}_diff"] = predictor[feature] - predictor[f"Opp_{feature}"]

    return predictor

def add_statistics(team1, team1_data, team2, team2_data, kenpom):

    # Converts team names to sports-reference
    team1_data = pretournament_stats.kenpom_to_sports_ref_df(team1_data)
    team2_data = pretournament_stats.kenpom_to_sports_ref_df(team2_data)

    # Converts user entered name to sports-reference
    team1 = pretournament_stats.kenpom_to_sports_ref(team1)
    team2 = pretournament_stats.kenpom_to_sports_ref(team2)

    # Initialize empty stat dataframes
    team1_df = pd.DataFrame(columns=["Team", "team_game_result", "fg_pct", "fg3_pct", "ft_pct", "efg_pct", "fga",
                                     "fg3a", "fta", "orb", "drb", "tov","opp_name_abbr", "pt_diff"])
    team2_df = pd.DataFrame(columns=["Team", "team_game_result", "fg_pct", "fg3_pct", "ft_pct", "efg_pct", "fga",
                                     "fg3a", "fta", "orb", "drb", "tov","opp_name_abbr", "pt_diff"])

    # Get stats for dataframes
    team1_df = pretournament_stats.team_stats(team1, year="2025", index=0, stat_df=team1_df)
    team2_df = pretournament_stats.team_stats(team2, year="2025", index=0, stat_df=team2_df)

    # Merge kenpom and sports-reference dataframes
    team1_data = pd.merge(team1_data, team1_df, on="Team", how="inner")
    team2_data = pd.merge(team2_data, team2_df, on="Team", how="inner")

    # Take average of pt_diff (across 5 games)
    team1_data["pt_diff"] = team1_data["pt_diff"] / 5
    team2_data["pt_diff"] = team2_data["pt_diff"] / 5

    # Calculate average net of past 5 games
    team1_data["last_5_avg_net"] = combine_data.get_average_net(team1_data, index=0, kenpom=kenpom, year="2025")
    team2_data["last_5_avg_net"] = combine_data.get_average_net(team2_data, index=0, kenpom=kenpom, year="2025")

    # Weight all neccessary stats
    team1_data = combine_data.weight_stats(team1_data)
    team2_data = combine_data.weight_stats(team2_data)

    # Convert names back to kenpom
    team1_data = pretournament_stats.sports_ref_to_kenpom(team1_data)
    team2_data = pretournament_stats.sports_ref_to_kenpom(team2_data)

    return team1_data, team2_data


main()