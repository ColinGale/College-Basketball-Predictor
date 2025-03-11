# College Basketball Tournament Predictor

This project is a **College Basketball Tournament Predictor** that uses **machine learning** to predict the outcome of Men's DI NCAA college basketball games with a focus on the NCAA National Tournament.
The model is trained on past tournament data and team statistics and is capable of predicting the winner of future matchups based on user input.

## Overview
The goal of this project is to build a machine learning model that can predict the outcome of **March Madness** basketball games based on team performance metrics. This project uses web scraping techniques to access 
the freely avaiable advanced stastics from *kenpom.com*, as well as historical tournament game result data from *sports-reference.com*. By taking in this data and merging it together, the project then uses 
a **Random Forest Classification**  model to make predictions. As of the most recent version of this predictor, the model has an **77.4% Accuracy Score** and a **77.4% Precision Score**. The model is trained on team and tournament 
data from 2018, 2019, 2022 and then is tested on the 2023 tournament results. This project also extracts data from the current 2025 season and allows the user to use the trained model to make predictions on the 2025 tournament to be played
in March of 2025.

---

## Use
This project offers a simple interface for the user to make a prediction of two teams facing off in the 2025 NCAA Tournament. The user must enter in the name of the both desired teams as they are listed on *kenpom.com* in order
to ensure proper functionality. Once this requirement has been satisfied, the model fits the data from both teams in order to make an accurate prediction of the outcome. The program prints out the result of the game so that the user
can clearly identify the winner. This project will be used to fill out a bracket in the nationwide **Men's Basketball Bracket Challenge** to see how the predictions compare to some of the best sports analysts in the world.

---

## What Data is Used to Make Predictions?

The model takes in a range of statistics pulled from both *kenpom.com* and *sports-reference.com* to make accurate predictions. Listed below are the names of each statistical category and what those names actually represent:

- **NetRtg**: Adjusted efficiency margin (KenPom)
- **ORtg**: Adjusted offensive efficiency margin; points scored per 100 possessions (KenPom)
- **DRtg**: Adjusted defensive efficiency margin; points allowed per 100 possessions (KenPom)
- **AdjT**: Adjusted tempo; possessions per 40 minutes (KenPom)
- **Luck**: Luck rating; deviation in winning percentage between a team’s actual record and their expected record (KenPom)
- **SOS_NetRtg**: Average adjusted efficiency margin of all opponents over a season (KenPom)
- **SOS_ORtg**: Average adjusted offensive efficiency margin of all opponents over a season (KenPom)
- **SOS_DRtg**: Average adjusted defensive efficiency margin of all opponents over a season (KenPom)
- **NCSOS_NetRtg**: Non conference strength of schedule ranking (KenPom)
- **Conf_code**: Numeric value that represents the conference a team plays in (KenPom)
- **W/L**: Wins and Losses for a season (KenPom)
- **Round**: The round of the tournament the game is being played (sports-reference)
-Seed: The seed in the tournament the team is (sports-reference)

*For all statistics above, the prefix **Opp_** refers to the opponent's statistics for the same category.

Names of the teams are not predictors for the model because the model is trained on tournment data across many years and College Basketball teams have frequent roster
changes indicating no pattern of strength. The conference is still included because from year to year the top basketball conferences usually remain the same.

---

## Features
- **Machine Learning Model**: Uses Random Forest Classifier to predict game outcomes.
- **Data Merging**: Combines team statistics with tournament results.
- **Matchup Predictions**: Allows the user to enter two teams and predict the winner.
- **Accuracy/Precision Reporting**: The model outputs its accuracy and precision based on historical test data.
- **Dynamic Predictions**: Makes predictions for the current year's tournament based on up-to-date team statistics.

---

## Acknowledgement

This project would not be possible without the amazing resources avaiable on **kenpom.com** and **sports-reference.com**. If you have an interest in more advanced college basketball statistics, please
check out these websites and support the creators. KenPom also offers a paid subscription for more advanced stats that are helpful to making your own college basketball predictions!

---

