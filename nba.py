import pandas as pd
import requests
from bs4 import BeautifulSoup


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



if __name__ == "__main__" :
    print(get_nba_radar('雷霆'))