import pandas as pd
import numpy as np

YEAR = '21'
PREV_YEAR = '20'
ACC_GAMES = 20
NUM_FANTASY_OWNERS = 9
THIS_YEAR_VS_LAST = 7
NUM_DRAFTED = 90

def main():
    df = pd.read_csv('players.csv')
    df = generatePredictions(df)
    df = generateValues(df)
    df = clean(df)
    df.to_csv('values.csv',index=False)

def generatePredictions(df):
    for i,row in df.iterrows():
        baseline = row['MP']
        if row['ACC_G'] > 0:
            ACC_MPG = row['ACC_MP'] / row['ACC_G']
            baseline = (baseline + ACC_MPG) / 2
        if np.isnan(row['MinKP120']):
            df.at[i,'PredMin'] = baseline
        else:
            df.at[i,'PredMin'] = (row['MinKP120'] + baseline)/2
    for i,row in df.iterrows():
        if np.isnan(row['PredMin']):
            continue
        m = row['MP']*row[f'G{YEAR}']
        mPrev = row[f'Min{PREV_YEAR}']*row[f'G{PREV_YEAR}']
        for cat in ['Pts','Reb','Ast']:
            c = row[cat]*row[f'G{YEAR}']
            cPrev = row[cat+PREV_YEAR]*row[f'G{PREV_YEAR}']
            if np.isnan(mPrev):
                if m == 0:
                    df.at[i,'Pred'+cat] = 0
                else:
                    df.at[i,'Pred'+cat]=((c)/m)*row['PredMin']
            else:
                if m == 0 and mPrev == 0:
                    df.at[i,'Pred'+cat] = 0
                else:
                    df.at[i,'Pred'+cat]=((c*THIS_YEAR_VS_LAST+cPrev)/(m*THIS_YEAR_VS_LAST+mPrev))*row['PredMin']
            # Adjust for games already played
            cACC = row[f'ACC_{cat}']
            gACC = row['ACC_G']
            cur_pred = df.at[i, f'Pred{cat}']
            df.at[i, f'Pred{cat}'] = (cur_pred * (ACC_GAMES - gACC) + cACC) / ACC_GAMES
    return df[~np.isnan(df['PredPts'])]

def generateValues(df):
    df['PrelimVal'] = 5*df['PredPts']+2.5*df['PredReb']+df['PredAst']
    df = df.nlargest(NUM_DRAFTED+10, 'PrelimVal')
    for cat in ['Pts','Reb','Ast']:
        m = np.mean(df['Pred'+cat])
        s = np.std(df['Pred'+cat])
        df[cat+'Val'] = (df['Pred'+cat]-m)/s
    df['Val'] = df['PtsVal']+df['RebVal']+df['AstVal']
    df = df.nlargest(NUM_DRAFTED, 'Val')
    for cat in ['Pts','Reb','Ast']:
        m = np.mean(df['Pred'+cat])
        s = np.std(df['Pred'+cat])
        df[cat+'Val'] = (df['Pred'+cat]-m)/s
    df['Val'] = df['PtsVal']+df['RebVal']+df['AstVal']
    df['Val'] -= np.min(df['Val'])
    df = df.sort_values('Val',ascending=False)
    df.loc[df['Val']<0,'Val'] = 0
    df['$$'] = (df['Val']/np.sum(df['Val']))*25*NUM_FANTASY_OWNERS
    return df

def clean(df):
    return df[['Name','Team','$$','PtsVal','RebVal','AstVal','PredPts','PredReb','PredAst','PredMin']].round(2)

main()
