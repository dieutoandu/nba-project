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

if __name__ == "__main__" :
    print(get_nba())