import pandas as pd
import numpy as np

def main():
    df = pd.read_csv('players.csv')
    df = generatePredictions(df)
    df = generateValues(df)
    df = clean(df)
    df.to_csv('values.csv',index=False)

def generatePredictions(df):
    for i,row in df.iterrows():
        if np.isnan(row['MinKP120']):
            df.at[i,'PredMin'] = row['MP']
        else:
            df.at[i,'PredMin'] = (row['MinKP120']*2+row['MP'])/3
    for i,row in df.iterrows():
        if np.isnan(row['PredMin']):
            continue
        m19 = row['MP']*row['G19']
        m18 = row['Min18']*row['G18']
        for cat in ['Pts','Reb','Ast']:
            c19 = row[cat]*row['G19']
            c18 = row[cat+'18']*row['G18']
            if np.isnan(m18):
                df.at[i,'Pred'+cat]=(c19/m19)*row['PredMin']
            else:
                df.at[i,'Pred'+cat]=((c19*3+c18)/(m19*3+m18))*row['PredMin']
    return df[~np.isnan(df['PredPts'])]

def generateValues(df):
    df['PrelimVal'] = 5*df['PredPts']+2.5*df['PredReb']+df['PredAst']
    df = df.nlargest(110,'PrelimVal')
    for cat in ['Pts','Reb','Ast']:
        m = np.mean(df['Pred'+cat])
        s = np.std(df['Pred'+cat])
        df[cat+'Val'] = (df['Pred'+cat]-m)/s
    df['Val'] = df['PtsVal']+df['RebVal']+df['AstVal']
    df = df.nlargest(100,'Val')
    for cat in ['Pts','Reb','Ast']:
        m = np.mean(df['Pred'+cat])
        s = np.std(df['Pred'+cat])
        df[cat+'Val'] = (df['Pred'+cat]-m)/s
    df['Val'] = df['PtsVal']+df['RebVal']+df['AstVal']
    df['Val'] -= np.min(df['Val'])
    df = df.sort_values('Val',ascending=False)
    df.loc[df['Val']<0,'Val'] = 0
    df['$$'] = (df['Val']/np.sum(df['Val']))*250
    return df

def clean(df):
    return df[['Name','Team','$$','PtsVal','RebVal','AstVal','PredPts','PredReb','PredAst','PredMin']].round(2)

main()
