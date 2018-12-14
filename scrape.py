from bs4 import BeautifulSoup
from urllib.request import urlopen
import pandas as pd
import numpy as np

def main():
    df = pd.DataFrame(columns=['Name','G19','Team','Pts','Reb','Ast','MP','MinKP120','Pts18','Reb18','Ast18','Min18','G18'])
    teams = ['virginia','duke','florida-state','north-carolina-state','virginia-tech','boston-college','north-carolina','syracuse','louisville','pittsburgh','clemson','notre-dame','georgia-tech','wake-forest','miami-fl']
    kp120teams = getKP120()
    for team in teams:
        df = loadTeam(team,df,kp120teams)
        print(df)
    df.to_csv('players.csv',index=False)
    #by drafted position, primary position
    #whether or not they made majors

def getKP120():
    url = 'https://kenpom.com'
    soup = BeautifulSoup(urlopen(url),features='lxml')
    kp120teams = set()
    for tr in soup.findAll('tr')[:126]:
        data = [td.getText() for td in tr.findAll('td')]
        if not data:
            continue
        kp120teams.add(data[1])
    return kp120teams 

def loadTeam(team,df,kp120teams):
    url = 'https://www.sports-reference.com/cbb/schools/{}/2019.html'.format(team)
    soup = BeautifulSoup(urlopen(url),features='lxml')
    count = 0
    for tr in soup.findAll('tr')[1:]:
        links = tr.findAll('a')
        if not links:
            if count==0:
                continue
            break
        count+=1
        pts18 = np.nan
        reb18 = np.nan
        ast18 = np.nan
        min18 = np.nan
        g18 = 0
        pts = np.nan
        reb = np.nan
        ast = np.nan
        mins = np.nan
        g19 = 0
        mp = np.nan
        MinKP120 = np.nan
        name = links[0].getText()
        add = links[0]['href']
        purl = 'https://www.sports-reference.com{}'.format(add)
        glogurl = '{}/gamelog/2019'.format(purl[:-5])
        psoup = BeautifulSoup(urlopen(purl),features='lxml')
        gsoup = BeautifulSoup(urlopen(glogurl),features='lxml')
        for tr in psoup.findAll('tr')[1:]:
            data = [td.getText() for td in tr.findAll('td')]
            links = tr.findAll('a')
            if not links:
                break
            year = links[0].getText()[-2:]
            if year == '19':
                g19 = float(data[2])
                mp = float(data[4])
                reb = float(data[19])
                ast = float(data[20])
                pts = float(data[25])
            elif year == '18':
                g18 = float(data[2])
                min18 = float(data[4])
                reb18 = float(data[19])
                ast18 = float(data[20])
                pts18 = float(data[25])
        gp = 0
        minp = 0
        for tr in gsoup.findAll('tr')[1:]:
            data = [td.getText() for td in tr.findAll('td')]
            if data[3] in kp120teams:
                gp+=1
                minp+=float(data[7])
        if gp:
            MinKP120 = minp/gp
        df = df.append({'Name':name,'G19':g19,'Pts':pts,'Reb':reb,'Ast':ast,'MP':mp,'MinKP120':MinKP120,'Pts18':pts18,'Reb18':reb18,'Ast18':ast18,'Min18':min18,'Team':team,'G18':g18},ignore_index=True)
    return df

main()
