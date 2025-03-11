import pandas as pd
from src.kenpom_data import all_years as all_years_kenpom
from tournament_data import all_years as all_years_tournament
from sklearn.ensemble import RandomForestClassifier


def main():
    # Data to train and test the model
    merged = merge_all_data(all_years_kenpom[:-1], all_years_tournament)

    # Team statistics to make new predictions for user input
    kenpom_2025 = all_years_kenpom[-1]

    # Preparing team statistics from current year
    columns_to_int = ["Rk", "W", "L"]
    columns_to_float = ["NetRtg", "ORtg", "DRtg", "AdjT", "Luck", "SOS_NetRtg", "SOS_ORtg", "SOS_DRtg", "NCSOS_NetRtg"]
    kenpom_2025 = prepare_dataframe(kenpom_2025, columns_to_float, columns_to_int)

    # Data that the model uses to determine results
    predictors = ["Conf_code", "NetRtg", "ORtg", "DRtg", "AdjT", "Luck", "SOS_NetRtg", "SOS_ORtg", "SOS_DRtg",
                  "NCSOS_NetRtg", "W", "L", "Seed", "NetRtg_diff", "NetRtg_ratio", "ORtg_diff", "ORtg_ratio", "DRtg_diff", "DRtg_ratio",
                  "AdjT_ratio", "AdjT_diff", "Luck_diff", "Luck_ratio", "SOS_NetRtg_diff", "SOS_NetRtg_ratio", "SOS_ORtg_diff", "SOS_ORtg_ratio",
                  "SOS_DRtg_diff", "SOS_DRtg_ratio", "NCSOS_NetRtg_diff", "NCSOS_NetRtg_ratio", "Opp_W", "Opp_L", "Opp_Seed", "Round"]

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
        team2 = input("Enter their opponent: ")

        predictor = predict_matchup(team1, team2, kenpom_2025)

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







def merge_all_data(all_years_kenpom, all_years_tournament):
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
        opponent_stats_columns = ["Team"] + columns_to_float + ["Rk", "W", "L", "Seed"]
        opponent_stats = merged[opponent_stats_columns].copy()

        # Rename the columns for the opponent stats
        for column in range(len(opponent_stats_columns)):
            if column != 0:
                opponent_stats.columns.values[column] = "Opp_" + opponent_stats.columns[column]
            else:
                opponent_stats.columns.values[column] = "Opponent"

        # Merge the opponent stats
        merged = pd.merge(merged, opponent_stats, on="Opponent", how="inner")

        # Matchup diff and ratio (helps with precision and accuracy being the same)
        matchup_features = ["NetRtg", "ORtg", "DRtg", "AdjT", "Luck", "SOS_NetRtg", "SOS_ORtg", "SOS_DRtg", "NCSOS_NetRtg"]
        for feature in matchup_features:
            merged[f"{feature}_diff"] = merged[feature] - merged[f"Opp_{feature}"]
            merged[f"{feature}_ratio"] = merged[feature] / (merged[f"Opp_{feature}"] + 1e-9)

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



def predict_matchup(team1, team2, kenpom):
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

    # Rename columns in team2_data to represent "Opponent"
    team2_data.columns = ["Opp_" + col if col != "Team" else "Opponent" for col in team2_data.columns]


    # Combine both teams into one DataFrame
    predictor = pd.concat([team1_data.reset_index(drop=True), team2_data.reset_index(drop=True)], axis=1)

    # Matchup diff and ratio (helps with precision and accuracy being the same)
    matchup_features = ["NetRtg", "ORtg", "DRtg", "AdjT", "Luck", "SOS_NetRtg", "SOS_ORtg", "SOS_DRtg", "NCSOS_NetRtg"]
    for feature in matchup_features:
        predictor[f"{feature}_diff"] = predictor[feature] - predictor[f"Opp_{feature}"]
        predictor[f"{feature}_ratio"] = predictor[feature] / predictor[f"Opp_{feature}"]

    predictor.to_csv("test2.csv")
    print(predictor)

    # Manually set Seed/Round to 1
    predictor["Seed"] = 1
    predictor["Opp_Seed"] = 1
    predictor["Round"] = 1

    return predictor


main()