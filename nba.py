import pandas as pd
import requests
from bs4 import BeautifulSoup
import lxml
import pymysql
import re
from datetime import datetime
from dotenv import load_dotenv
import os


def get_nba():
    url="https://tw-nba.udn.com/nba/stats/teams"
    resp=requests.get(url)
    soup=BeautifulSoup(resp.text,'lxml')
    columns=[i.text for i in soup.find("table",class_="stable matchup standings sortable").find_all('tr')[0].find_all("th")]
    datas=[i.text.split() for i in soup.find("table",class_="stable matchup standings sortable").find_all('tr')[1:]]
    
    df=pd.DataFrame(datas,columns=columns)
    df=df.dropna()
    
    datas=df.values.tolist()
    teams=df['球隊'].values.tolist()[:-1]


    x_data=df['球隊'].values.tolist()[:-1]
    y_data=df['投籃'].astype(float).values.tolist()
    y2_data=df['得分'].astype(float).values.tolist()
    y3_data=df['命中率'].str.replace('%', '').astype(float).values.tolist()


    return datas,columns, teams, x_data,y_data , y2_data, y3_data


def get_player(team):
    url="https://tw-nba.udn.com/nba/stats/teams"
    resp=requests.get(url)
    soup=BeautifulSoup(resp.text,'lxml')
    player_url={i.find('a').text:"https://tw-nba.udn.com"+i.find('a').get('href') for i in soup.find("table",class_="stable matchup standings sortable").find_all('tr')[1:-1]}

    if team in player_url:
        url_w=player_url[team]
        resp_w=requests.get(url_w)
        soup_w=BeautifulSoup(resp_w.text,'lxml')
        player_columns=[i.text for i in soup_w.find('table',class_="stable matchup sortable").find_all('th')]
        player_values=[i.text.strip().split('\n') for i in soup_w.find('table',class_="stable matchup sortable").find_all('tr')[1:]]

        df=pd.DataFrame(player_values,columns=player_columns).dropna()
        x_data=df['姓名'].values.tolist()
        y_data=df['上場數'].astype(int).values.tolist()
        y2_data=df['場均時間'].astype(float).values.tolist()
        y3_data=df['平均得分'].astype(float).values.tolist()


        
    return player_columns,player_values,x_data,y_data,y2_data,y3_data


def get_nba_radar(team):
    url="https://tw-nba.udn.com/nba/stats/teams"
    resp=requests.get(url)
    soup=BeautifulSoup(resp.text,'lxml')
    columns=[i.text for i in soup.find("table",class_="stable matchup standings sortable").find_all('tr')[0].find_all("th")]
    datas=[i.text.split() for i in soup.find("table",class_="stable matchup standings sortable").find_all('tr')[1:]]
    df=pd.DataFrame(datas,columns=columns)
    df=df.dropna()

    score=[]
    df_1=df[["球隊","進攻籃板","防守籃板","籃粄","助攻","失誤","抄截"]]
    radars=[{i[0]: i[1:]} for i in df_1.values.tolist()]
    for radar in radars:
        if team in radar:
            score=[float(i) for i in radar[team]]
            
            

    return score

def get_all_player():
    columns,datas=None,None
    conn=None
    try:
        conn=open_db()
        cur=conn.cursor()
        sqlstr="select * from all_player"
        cur.execute(sqlstr)
        columns=[col[0] for col in cur.description]
        datas=cur.fetchall()

    except Exception as e :
        print(e)
    finally:
        if conn is not None:
            conn.close()
    
    return columns,datas


def get_player_url(lis):
    datas=[]
    conn=None
    try:
        conn=open_db()
        cur=conn.cursor()
        for i in lis:
            data=None
            sqlstr="select * from all_player_url where name= %s"
            cur.execute(sqlstr,(i,))
            
            data = cur.fetchall()
            datas.extend(data)

    except Exception as e :
        print(e)
    finally:
        if conn is not None:
            conn.close()
    
    return datas

def eff(df):
    df['場均時間']=df['場均時間'].astype(float)
    df['平均得分']=df['平均得分'].astype(float)
    df['籃板']=df['籃板'].astype(float)
    df['助攻']=df['助攻'].astype(float)
    df['抄截']=df['抄截'].astype(float)
    df['阻攻']=df['阻攻'].astype(float)
    df['投籃命中率']=df['投籃命中率'].replace('%', '').astype(float)
    df['三分命中率']=df['三分命中率'].replace('%', '').astype(float)
    df['罰球命中率']=df['罰球命中率'].replace('%', '').astype(float)
    df['失誤']=df['失誤'].astype(int)
    df['犯規']=df['犯規'].astype(int)
    eff = (
            df['平均得分']* 1.0 +
            df['籃板']* 1.2 +
            df['助攻']* 1.5 +
            df['抄截']* 2.0 +
            df['阻攻']* 2.0 -
            (df['失誤']* 1.00 / df['上場數'])
        ).fillna(0).round(2).astype(float)
    return eff.values.tolist()

load_dotenv('.env')
def open_db():
    conn=None

    try:
        conn=pymysql.connect(
        host=os.environ.get("DB_HOST"),
        port=int(os.environ.get("DB_PORT")),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        db=os.environ.get("DB_NAME")
        )
    except Exception as e :
        print("open_db erro : ",e )

    return conn


def parse_height_weight(text):
    # 用正則抓出英尺、英寸與磅數
    match = re.search(r"(\d+)’(\d+)＂/(\d+)", text)
    if not match:
        return None
    
    feet = int(match.group(1))
    inches = int(match.group(2))
    pounds = int(match.group(3))

    # 身高換算：1 英尺 = 30.48 cm, 1 英寸 = 2.54 cm
    height_cm = round(feet * 30.48 + inches * 2.54, 1)

    # 體重換算：1 磅 = 0.453592 kg
    weight_kg = round(pounds * 0.453592, 1)

    return [height_cm, weight_kg]


def calculate_age(birthdate_str):
    if "：" in birthdate_str:
        birthdate_str = birthdate_str.split("：")[1]
        
    birthdate = datetime.strptime(birthdate_str, "%Y-%m-%d")
    today = datetime.today()
    
    age = today.year - birthdate.year
    # 如果今年生日還沒到，要減 1
    if (today.month, today.day) < (birthdate.month, birthdate.day):
        age -= 1

    return [age]


def get_all_player_url():
    url="https://tw-nba.udn.com/nba/stats/teams"
    resp=requests.get(url)
    soup=BeautifulSoup(resp.text,'lxml')
    player_url={i.find('a').text:"https://tw-nba.udn.com"+i.find('a').get('href') for i in soup.find("table",class_="stable matchup standings sortable").find_all('tr')[1:-1]}

    all_player=[]
    for i in player_url:
        resp_w=requests.get(player_url[i])
        soup_w=BeautifulSoup(resp_w.text,'lxml')
        for i in soup_w.find('table',class_="stable matchup sortable").find_all("tr")[1:]:
            nba_player={j.text:j.get("href") for j in i.find_all("a")}
            #print(nba_player)
            all_player.append(nba_player)
    
    return all_player




if __name__ == "__main__" :
    test=['Donovan Mitchell','Darius Garland','Evan Mobley','Max Strus','Trent Forrest']
    print(get_player_url(test))