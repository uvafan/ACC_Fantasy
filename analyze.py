import pandas as pd
import numpy as np

def main():
    df = pd.read_csv('players.csv')
    df = generatePredictions(df)
    df = generateValues(df)
    df = clean(df)
    df.to_csv('values.csv',index=False)

def generatePredictions(df):
    df['PredPTS'] = df['Pts'] 
    df['PredREB'] = df['Reb'] 
    df['PredAST'] = df['Ast']
    return df[~np.isnan(df['PredPTS'])]

def generateValues(df):
    df['PrelimVal'] = 5*df['PredPTS']+2.5*df['PredREB']+df['PredAST']
    df = df.nlargest(100,'PrelimVal')
    for cat in ['PTS','REB','AST']:
        m = np.mean(df['Pred'+cat])
        s = np.std(df['Pred'+cat])
        df[cat+'Val'] = (df['Pred'+cat]-m)/s
    df['Val'] = df['PTSVal']+df['REBVal']+df['ASTVal']
    df2 = df.nlargest(90,'Val')
    df['Val'] -= np.min(df2['Val'])
    df = df.sort_values('Val',ascending=False)
    df.loc[df['Val']<0,'Val'] = 0
    df['$$'] = (df['Val']/np.sum(df['Val']))*250
    return df

def clean(df):
    return df[['Name','Team','$$','PTSVal','REBVal','ASTVal','PredPTS','PredREB','PredAST']].round(2)

main()
