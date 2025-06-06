from flask import Flask, render_template, request
import pandas as pd
import json
from nba import get_nba, get_player,get_nba_radar,get_all_player,eff,get_player_url,calculate_age,parse_height_weight
from bs4 import BeautifulSoup
import requests
import lxml


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
        df=df.sort_values(by=player_data,ascending=False)[:10]
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
    datas=[]
    all_player_body=[]
    formatted_body = """
        <div class="player-card">
        </div>
        """
    if player_data in df.columns.tolist():
        df=df.sort_values(by=player_data,ascending=False)[:10]
        score=df[['平均得分','籃板','助攻','抄截','阻攻','失誤']].astype(float).values.tolist()
        player_name=df['姓名'].values.tolist()
        datas=get_player_url(player_name)

        
        for i in datas:
            n_player=[]
            resp_p=requests.get(i[2])
            soup_p=BeautifulSoup(resp_p.text,'lxml')
            player=soup_p.find('div',class_="team_head").text.replace(" ","").split()
            n_player.append(player[0])# 姓名
            n_player.append(player[1])#隊伍
            n_player.append(player[2])#位置
            n_player+=parse_height_weight(player[3])#身高體重
            n_player+=calculate_age(player[4])#年齡
            all_player_body.append(n_player)
        
        for p in all_player_body:
            formatted_body += f"""
            <div class="player-card">
                <strong>姓名:</strong> {p[0]}<br>
                <strong>{p[1]}</strong> <br>
                <strong>{p[2]}</strong> <br>
                <strong>身高:</strong> {p[3]}<br>
                <strong>體重:</strong> {p[4]}<br>
                <strong>年齡:</strong> {p[5]}<br>
                <hr>
            </div>
            """
        


    
    return json.dumps({"score":score,"player_name":player_name,"all_player_body":formatted_body})




if __name__ == "__main__":
    app.run(debug=False)
