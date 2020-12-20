from bs4 import BeautifulSoup
from urllib.request import urlopen
import pandas as pd
import numpy as np

YEAR = '21'
PREV_YEAR = '20'

ACC_Teams_SR = ['Louisville', 'Duke', 'Virginia', 'UNC', 'Georgia Tech', 'Boston College', 'Pitt', 'Virginia Tech', 'Florida State', 'NC State', 'Notre Dame', 'Clemson', 'Miami (FL)', 'Wake Forest', 'Syracuse']

def main():
    df = pd.DataFrame(columns=['Name','G'+YEAR,'Team','Pts','Reb','Ast','MP','MinKP120','Pts'+PREV_YEAR,'Reb'+PREV_YEAR,'Ast'+PREV_YEAR,'Min'+PREV_YEAR,'G'+PREV_YEAR,'ACC_G','ACC_Pts','ACC_Reb','ACC_Ast', 'ACC_MP'])
    teams = ['virginia','duke','florida-state','north-carolina-state','virginia-tech','boston-college','north-carolina','syracuse','louisville','pittsburgh','clemson','notre-dame','georgia-tech','wake-forest','miami-fl']
    kp120teams = getKP120()
    for team in teams:
        df = loadTeam(team,df,kp120teams)
        print(df)
    df.to_csv('players.csv',index=False)

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
    url = 'https://www.sports-reference.com/cbb/schools/{}/20{}.html'.format(team, YEAR)
    soup = BeautifulSoup(urlopen(url),features='lxml')
    count = 0
    for tr in soup.findAll('tr')[1:]:
        links = tr.findAll('a')
        if not links:
            if count==0:
                continue
            break
        count += 1
        ptsPrev = np.nan
        rebPrev = np.nan
        astPrev = np.nan
        minPrev = np.nan
        gPrev = 0
        pts = np.nan
        reb = np.nan
        ast = np.nan
        mins = np.nan
        g = 0
        mp = np.nan
        MinKP120 = np.nan
        name = links[0].getText()
        add = links[0]['href']
        purl = 'https://www.sports-reference.com{}'.format(add)
        glogurl = '{}/gamelog/20{}'.format(purl[:-5],YEAR)
        psoup = BeautifulSoup(urlopen(purl),features='lxml')
        gsoup = BeautifulSoup(urlopen(glogurl),features='lxml')
        for tr in psoup.findAll('tr')[1:]:
            data = [td.getText() for td in tr.findAll('td')]
            links = tr.findAll('a')
            if not links:
                break
            year = links[0].getText()[-2:]
            if year == YEAR:
                g = float(data[2])
                mp = float(data[4])
                reb = float(data[19])
                ast = float(data[20])
                pts = float(data[25])
            elif year == PREV_YEAR and len(data) > 25 and float(data[2]) > 0:
                gPrev = float(data[2])
                minPrev = float(data[4])
                rebPrev = float(data[19])
                astPrev = float(data[20])
                ptsPrev = float(data[25])
        gp = 0
        minp = 0
        ptsACC = 0
        rebACC = 0
        astACC = 0
        minACC = 0
        gACC = 0
        for tr in gsoup.findAll('tr')[1:]:
            data = [td.getText() for td in tr.findAll('td')]
            if data[3] in kp120teams:
                gp+=1
                minp+=float(data[7])
            if data[3] in ACC_Teams_SR:
                gACC += 1
                minACC += float(data[7])
                rebACC += float(data[22])
                astACC += float(data[23])
                ptsACC += float(data[28])
        if gp:
            MinKP120 = minp/gp
        df = df.append({'Name':name,'G'+YEAR:g,'Pts':pts,'Reb':reb,'Ast':ast,'MP':mp,'MinKP120':MinKP120,'Pts'+PREV_YEAR:ptsPrev,'Reb'+PREV_YEAR:rebPrev,'Ast'+PREV_YEAR:astPrev,'Min'+PREV_YEAR:minPrev,'Team':team,'G'+PREV_YEAR:gPrev, 'ACC_G':gACC, 'ACC_Pts': ptsACC, 'ACC_Reb': rebACC, 'ACC_Ast': astACC, 'ACC_MP': minACC},ignore_index=True)

    return df

main()
