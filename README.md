# 🏀 College Basketball Tournament Predictor

This project is a **College Basketball Tournament Predictor** that leverages **machine learning** to predict the outcomes of NCAA Division I Men's Basketball Tournament games. By analyzing historical tournament data and team statistics, the model provides insights into potential winners based on user input.

---

## 📌 Overview
The goal of this project is to develop a predictive model for **March Madness** matchups using advanced team performance metrics. The model is trained using:
- **Advanced team statistics** from [kenpom.com](https://kenpom.com)
- **Historical tournament game results** from [sports-reference.com](https://www.sports-reference.com)

A **Random Forest Classifier** is employed to make predictions, utilizing tournament data from **2018, 2019, and 2022** for training and testing against **2023** results. The model also integrates **2025 season data**, allowing users to forecast tournament outcomes for the current year.

**📊 Model Performance:**  
✔️ **Accuracy:** 80.6%  
✔️ **Precision:** 80.6%

---

## 🎮 How to Use
This project provides an intuitive interface for users to predict matchups in the **2025 NCAA Tournament**. To make a prediction:
1. Enter the names of two teams as listed on [kenpom.com](https://kenpom.com).
2. The model processes both teams' statistics.
3. The predicted winner is displayed clearly for easy interpretation.

This predictor will be used to generate a full tournament bracket and compare results against expert analysts in the **Men's Basketball Bracket Challenge**.

> **Note:** The script `pretournament_stats.py` collects data from the last 5 games of each team before the tournament. To respect *sports-reference.com*’s request limits, this data is stored locally in respective CSV file (team_data_year.csv) and is **not run in the main program**. Running the script manually takes approximately **12 minutes**.

---

## 📊 Data Used for Predictions
The model relies on a set of key basketball statistics sourced from *kenpom.com* and *sports-reference.com*. Below is an overview of these statistics:

### **🔹 Team Performance Metrics (KenPom)**
- **NetRtg** – Adjusted efficiency margin
- **ORtg** – Offensive efficiency (points per 100 possessions)
- **DRtg** – Defensive efficiency (points allowed per 100 possessions)
- **AdjT** – Adjusted tempo (possessions per 40 minutes)
- **Luck** – Deviation between actual and expected record
- **SOS_NetRtg** – Strength of schedule (efficiency margin)
- **SOS_ORtg** – Strength of schedule (offensive efficiency)
- **SOS_DRtg** – Strength of schedule (defensive efficiency)
- **NCSOS_NetRtg** – Non-conference strength of schedule ranking
- **W/L** – Win-loss record

### **🔹 Tournament-Specific Metrics (Sports-Reference)**
- **Round** – The tournament round the game is played in
- **Seed** – The team’s seed in the tournament
- **last_5_avg_net** – Average NetRtg of opponents in the last 5 games
- **efg_pct** – Weighted effective field goal percentage in last 5 games vs. season average
- **fg3_pct** – Weighted 3-point field goal percentage in last 5 games vs. season average
- **tov** – Weighted turnovers per game in last 5 games vs. season average
- **pt_diff** – Average point differential in last 5 games

📌 **Important:** The model predicts using **statistical differentials** (_diff), meaning it only considers the difference between teams' stats rather than absolute values. This minimizes bias caused by team names, as rosters frequently change from year to year.

---

## 🔥 Features
✅ **Machine Learning Model** – Utilizes Random Forest Classifier for game outcome prediction.  
✅ **Data Integration** – Combines team statistics with historical tournament results.  
✅ **Matchup Predictions** – Allows users to input two teams and receive a game outcome prediction.  
✅ **Performance Reporting** – Displays accuracy and precision based on test data.  
✅ **Dynamic 2025 Predictions** – Uses up-to-date statistics for real-time forecasting.  

---

## 🙌 Acknowledgements
This project was made possible thanks to the fantastic resources provided by **[KenPom](https://kenpom.com)** and **[Sports-Reference](https://www.sports-reference.com)**. If you're interested in advanced college basketball analytics, consider supporting these platforms. KenPom also offers a paid subscription for in-depth statistical insights to improve your own predictions!

---

🏀 **May your brackets be ever in your favor!** 🎉

