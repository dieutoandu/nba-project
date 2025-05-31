from flask import Flask, render_template, request
import pandas as pd
import json
from nba import get_nba, get_player,get_nba_radar,get_all_player,eff
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


@app.route("/all-player")
def open_all_player():
    
    columns,datas=get_all_player()

    df=pd.DataFrame(datas,columns=columns)

    df.columns = ['id','姓名', '位置', '上場數', '場均時間', '平均得分', '籃板', '助攻', '抄截', '阻攻','投籃命中率', '三分命中率', '罰球命中率', '失誤', '犯規']

    EFF=eff(df)
    all_player_name=df['姓名'].values.tolist()

    datas=df.values.tolist()
    columns=df.columns.tolist()

    return render_template('all-player.html',columns=columns,datas=datas,y_data=EFF,x_data=all_player_name)

@app.route("/get_player_data")
def player_data():
    
    player_data = request.args.get("columns", "all")

    columns,datas=get_all_player()
    df=pd.DataFrame(datas,columns=columns)
    df.columns = ['id','姓名', '位置', '上場數', '場均時間', '平均得分', '籃板', '助攻', '抄截', '阻攻','投籃命中率', '三分命中率', '罰球命中率', '失誤', '犯規']

    if player_data in df.columns.tolist():
        df=df.sort_values(by=player_data,ascending=False)[:5]
        all_player_name=df['姓名'].values.tolist()
        EFF=eff(df)
        # print(df)
        # print(df.info())
        
        datas=df.astype(str).values.tolist()

    else:
        EFF=eff(df)
        datas=df.astype(str).values.tolist()
        all_player_name=df['姓名'].values.tolist()
    columns=df.columns.tolist()

    return json.dumps({"datas":datas,"y_data":EFF,"x_data":all_player_name})


@app.route("/get_player_radar")
def player_radar():

    player_data = request.args.get("columns", "all")

    columns,datas=get_all_player()
    df=pd.DataFrame(datas,columns=columns)
    df.columns = ['id','姓名', '位置', '上場數', '場均時間', '平均得分', '籃板', '助攻', '抄截', '阻攻','投籃命中率', '三分命中率', '罰球命中率', '失誤', '犯規']

    score=[]
    player_name=[]
    if player_data in df.columns.tolist():
        df=df.sort_values(by=player_data,ascending=False)[:5]
        score=df[['平均得分','籃板','助攻','抄截','阻攻','失誤']].astype(float).values.tolist()
        player_name=df['姓名'].values.tolist()
    
    return json.dumps({"score":score,"player_name":player_name})


if __name__ == "__main__":
    app.run(debug=True)
