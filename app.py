from flask import Flask, render_template, request
import pandas as pd
import json
from nba import get_nba, get_player,get_nba_radar
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

    
    datas, columns, teams, x_data, y_data, y2_data, y3_data = get_nba()
    
    df = pd.DataFrame(datas, columns=columns)
    df = df.dropna()

    if team != "all":
        
        player_columns, player_values ,x_data,y_data,y2_data,y3_data = get_player(team)
        df = pd.DataFrame(player_values, columns=player_columns)

    return json.dumps({"datas": df.values.tolist(), "columns": df.columns.tolist() , "x_data":x_data, "y_data":y_data ,"y2_data":y2_data,"y3_data":y3_data})


@app.route("/get_team_radar")
def get_radar():
    team = request.args.get("team", "all")
    radar=[0,0,0,0,0]

    if team != "all":
        radar=get_nba_radar(team)
    
    return json.dumps({"radar":radar})



if __name__ == "__main__":
    app.run(debug=True)
