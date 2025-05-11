from flask import Flask ,render_template,request
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json


app= Flask(__name__)

@app.route("/")
def index():
    url="https://tw-nba.udn.com/nba/stats/teams"
    resp=requests.get(url)
    soup=BeautifulSoup(resp.text,'lxml')
    columns=[i.text for i in soup.find("table",class_="stable matchup standings sortable").find_all('tr')[0].find_all("th")]
    datas=[i.text.split() for i in soup.find("table",class_="stable matchup standings sortable").find_all('tr')[1:]]
    
    df=pd.DataFrame(datas,columns=columns)
    df=df.dropna()
    
    datas=df.values.tolist()
    teams=df['球隊'].values.tolist()[:-1]



    return render_template("index.html",datas=datas ,columns=columns,teams=teams)


@app.route("/get_team_data_table")
def get_team_data_table():
    team = request.args.get("team", "all")

    
    url = "https://tw-nba.udn.com/nba/stats/teams"
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'lxml')
    columns=[i.text for i in soup.find("table",class_="stable matchup standings sortable").find_all('tr')[0].find_all("th")]
    datas=[i.text.split() for i in soup.find("table",class_="stable matchup standings sortable").find_all('tr')[1:]]
    df = pd.DataFrame(datas, columns=columns)
    df = df.dropna()

    if team != "all":
        df = df[df["球隊"] == team]

    return json.dumps({"datas": df.values.tolist()})






if __name__ == "__main__":
    app.run(debug=True)