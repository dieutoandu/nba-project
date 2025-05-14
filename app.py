from flask import Flask, render_template, request
import pandas as pd
import json
from nba import get_nba, get_player
from bs4 import BeautifulSoup
import requests


app = Flask(__name__)


@app.route("/")
def index():
    datas, columns, teams, x_data, y_data, y2_data, y3_data = get_nba()

    return render_template(
        "index.html",
        datas=datas,
        columns=columns,
        teams=teams,
        x_data=x_data,
        y_data=y_data,
        y2_data=y2_data,
        y3_data=y3_data,
    )


@app.route("/get_team_data_table")
def get_team_data_table():
    team = request.args.get("team", "all")

    url = "https://tw-nba.udn.com/nba/stats/teams"
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "lxml")
    columns = [
        i.text
        for i in soup.find("table", class_="stable matchup standings sortable")
        .find_all("tr")[0]
        .find_all("th")
    ]
    datas = [
        i.text.split()
        for i in soup.find(
            "table", class_="stable matchup standings sortable"
        ).find_all("tr")[1:]
    ]
    datas, columns, teams, x_data, y_data, y2_data, y3_data = get_nba()
    df = pd.DataFrame(datas, columns=columns)
    df = df.dropna()

    if team != "all":
        
        player_columns, player_values ,x_data,y_data,y2_data,y3_data = get_player(team)
        df = pd.DataFrame(player_values, columns=player_columns)

    return json.dumps({"datas": df.values.tolist(), "columns": df.columns.tolist() , "x_data":x_data, "y_data":y_data ,"y2_data":y2_data,"y3_data":y3_data})


if __name__ == "__main__":
    app.run(debug=True)
