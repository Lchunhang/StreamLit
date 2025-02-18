#!/usr/bin/env python
# coding: utf-8

# In[35]:

#Packages
import pandas as pd
from scipy.stats import zscore
import numpy as np
import ipywidgets as widgets
from mplsoccer import PyPizza
import warnings
import streamlit as st
from sklearn import preprocessing
from streamlit import components
import os
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import altair as alt

hide_github_icon = """
<style>
.css-1jc7ptx, .e1ewe7hr3, .viewerBadge_container__1QSob, .styles_viewerBadge__1yB5_, .viewerBadge_link__1S137, .viewerBadge_text__1JaDK{ display: none; } #MainMenu{ visibility: hidden; } footer { visibility: hidden; } header { visibility: hidden; }
</style>
"""
st.markdown(hide_github_icon,unsafe_allow_html=True)

st.markdown("""
        <style>
               .block-container {
                    padding-top: 0rem;
                    padding-bottom: 0rem;
                    padding-right: 1rem;
                }
        </style>
        """, unsafe_allow_html=True)

#Remove Warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)
pd.options.mode.chained_assignment = None 

st.markdown('<p style="font-size: 60px; font-weight: bold;">Role Ranking System</p>', unsafe_allow_html=True)
st.markdown('<p style="font-weight:bold; font-size: 20px; color: #808080;">By Chun Hang (<a href="https://twitter.com/chunhang7" target="_blank">Twitter</a> & <a href="https://www.instagram.com/chunhang7/" target="_blank">Instagram</a>): @chunhang7</p>', unsafe_allow_html=True)

with st.expander("App Details"):
    st.write('''
    The Role Ranking System assigns varrying weightages to different metrics based on their relevance to specific roles, reflecting the author's perspective backed by extensive research.\n 
    Similarity Function is based on K-Means Clustering, to identify similar players based on playstyle.\n
    
    Note: Only Outfielders from Top 777 Leagues with over 1080 Minutes Played in 2022/23 Season are Included for Selection.
    ''')
        
df = pd.read_csv("https://raw.githubusercontent.com/Lchunhang/StreamLit/main/FinalStats.csv")

df = df.loc[~(df['Position'] == 'Goalkeeper')]

#Attributes
#setting the factors
df['Minutes Normalized'] = ((df['Starts'] * 90  / df['Matches Played'] * 90) * df['Minutes Played'])
df['Total Possible Minutes'] = df['Matches Played'] * 90
df['Passing Factor'] = df['League Average Passes'] / df['Squad Total Completed Passes']
df['Crossing Factor'] = df['League Average Crosses'] / df['Squad Total Completed Crosses']

#Ball Winning
df['True Tackles per Oppo Touch'] = (df['Tackles'] + df['Fouls'] + df['Challenges Lost']) / df['Oppo Live Touches']
df['Tackles per Oppo Touch'] = df['Tackles'] / df['Oppo Live Touches']
df['True Tackles Win Rate'] = df['Tackles per Oppo Touch'] / df['True Tackles per Oppo Touch']
df['Interceptions per Oppo Touch'] = df['Interceptions'] / df['Oppo Live Touches']
df['1v1 Tackles per Oppo Touch'] = df['Dribblers Tackled'] / df['Oppo Live Touches']
df['True Interceptions per Oppo Touch'] = (df['Passes Blocked'] + df['Interceptions']) / df['Oppo Live Touches']
df['Att 3rd Tackles per Oppo Def 3rd Touch'] = df['Att 3rd Tackles'] / df['Oppo Def 3rd Touches']

#Sweeping
df['Clearances per Oppo Touch'] = df['Clearances'] / df['Oppo Live Touches']
df['Recoveries per Oppo Touch'] = df['Recoveries'] / df['Oppo Live Touches']
df['Blocks per Oppo Touch'] = df['Blocks'] / df['Oppo Live Touches']

#Carrying
df['Progressive Carries per Touch'] = df['Progressive Carries'] / df['Live Touches']
df['Successful Dribbles per Touch'] = df['Successful Dribbles'] / df['Live Touches']
df['Wide Progressive Carries per Touch'] = df['Wide Progressive Carries'] / df['Live Touches']
df['Central Progressive Carries per Touch'] = df['Central Progressive Carries'] / df['Live Touches']
df['Chance Creating Carries per Touch'] = df['Chance Creating Carries'] / df['Live Touches']
df['Carries Inwards per Touch'] = df['Carries Inwards'] / df['Live Touches']

#Passing
df['Normalized Progressive Passes'] = df['Progressive Passes'] * df['Passing Factor']
df['Normalized Central Progressive Passes'] = df['Central Progressive Passes'] * df['Passing Factor']
df['Normalized Completed Passes'] = df['Passes Completed'] * df['Passing Factor']
df['Normalized Crosses'] = df['Crosses'] * df['Crossing Factor']
df['Outward Distribution Rate'] = df['Outward Distribution'] * df['Passing Factor']
df['Normalized Half Space Passes'] = df['Half Space Passes'] * df['Passing Factor']

#Receiving
df['Normalized Progressive Passes Received'] = df['Progressive Passes Received'] / (df['Squad Total Completed Progressive Passes'] - df['Prog Passes']) 
df['Half-Space Passes Received Rate'] = df['Half Space Received'] / df['Passes Received']
df['Zone 14 Passes Received Rate'] = df['Zone 14 Received'] / df['Passes Received']
df['Wide Passes Received Rate'] = df['Wide Received'] / df['Passes Received']
df['Normalized Att Pen Touches'] = df['Att Pen Touches'] / df['Total Touches']

#Possession
df['Passes Received Rate'] = df['Passes Received'] / (df['Squad Total Completed Passes'] - df['Passes Completed'])
df['Carries Inwards per Touch'] = df['Carries Inwards'] / df['Live Touches']
df['Central Passes Received Rate'] = df['Central Received'] / df['Passes Received']
df['Defensive Third Touches Rate'] = df['Def 3rd Touches'] / df['Total Touches']

#Aerials
df['Aerial Duels Won'] = df['Aerial Duels Won'] 
df['Aerial Duels Won %'] = df['Aerial Duels Won %']

#Creation
df['Normalized Expected Assists'] = df['xA'] / df['Key Passes']
df['Shot-Creating Actions'] = df['SCA'] - df['SCA PassDead']
df['Normalized Key Passes'] = df['Key Passes'] / df['Passes Completed']

#Shooting
df['Shot-Ending Carries per Touch'] = df['Shot-Ending Carries'] / df['Live Touches']

#######################################################################

with st.sidebar:
    st.markdown('<h1 style="font-family: Consolas; font-size: 34px;">Select Your Players Here...</h1>', unsafe_allow_html=True)
    options = df["Player"].dropna().tolist()
    player = st.selectbox('Player', options)
    
    options2 = df["Position"].dropna().unique().tolist()
    default_position = df.loc[df['Player'] == player, 'Position'].values[0]
    user_input = st.selectbox("Enter Position Template (optional)", [default_position] + options2)

    if user_input != default_position:
        # Filter based on user input
        position = user_input
    else:
        # Default behavior with 'Position' derived from 'Player' column
        position = default_position

    # If the user has selected a position, update the position of the selected player
    if user_input != default_position:
        df.loc[df['Player'] == player, 'Position'] = position

    # Filter the dataframe based on the position
    df = df.loc[df['Position'] == position].reset_index(drop=True)
    st.write(position+" Template")
    st.markdown('<h1 style="font-family: Consolas; font-size: 34px;">..And Let The Magic Happen ➡️</h1>', unsafe_allow_html=True)

#Extract age, ready to merge
age = df[['Player','True Age', 'Minutes Played']]
age.rename(columns = {'True Age':'Age'},inplace = True)

# Note that `select_dtypes` returns a data frame. We are selecting only the columns
numeric_cols = df.select_dtypes(include=[np.number]).columns
df[numeric_cols] = df[numeric_cols].apply(zscore)

#Scale it to 100
x = df[numeric_cols]
min_max_scaler = preprocessing.MinMaxScaler()
x_scaled = min_max_scaler.fit_transform(x)
x_scaled = x_scaled *100
df[numeric_cols] = pd.DataFrame(x_scaled)

#######################################################################

def CB_Rating(df):
    df['Ball Winning Value'] = (df['True Tackles Win Rate']*35/100) + (df['Interceptions per Oppo Touch']*45/100) + (df['True Tackles per Oppo Touch']*20/100) 
    df['Ball Winning Rank'] = (((df['Ball Winning Value'].rank(pct=True))*99)).astype(int)

    df['Sweeping Value'] = (df['Blocks per Oppo Touch']*35/100) + (df['Recoveries per Oppo Touch']*30/100) + (df['Clearances per Oppo Touch']*35/100)
    df['Sweeping Rank'] = (((df['Sweeping Value'].rank(pct=True))*99)).astype(int)

    df['Carrying Value'] = (df['Progressive Carries per Touch']*50/100) + (df['Successful Dribbles per Touch']*30/100) + (df['Successful Dribbles %']*20/100)
    df['Carrying Rank'] = (((df['Carrying Value'].rank(pct=True))*99)).astype(int)

    df['Passing Value'] = (df['Normalized Progressive Passes']*30/100) + (df['Normalized Completed Passes']*40/100) + (df['Pass Completion %']*30/100)
    df['Passing Rank'] = (((df['Passing Value'].rank(pct=True))*99)).astype(int)

    df['Possession Value'] = (df['Central Passes Received Rate']*30/100) + (df['Post-Recovery Passes']*35/100) + (df['Passes Received Rate']*35/100)
    df['Possession Rank'] = (((df['Possession Value'].rank(pct=True))*99)).astype(int)

    df['Aerial Value'] = (df['Successful Defensive Aerials']*75/100) + (df['Aerial Duels Won %']*10/100) + (df['Successful Offensive Aerials']*15/100)
    df['Aerial Rank'] = (((df['Aerial Value'].rank(pct=True))*99)).astype(int)

    df['Minutes Normalized'] = (((df['Minutes Normalized'].rank(pct=True))*99)).astype(int)
    
    #Centre-Back Ratings
    df['Ball-Playing CB'] = (((((df['Minutes Normalized']*20/100) + (df['Ball Winning Value']*10/100) + (df['Sweeping Value']*10/100) + (df['Passing Value']*27/100) + (df['Possession Value']*21/100) + (df['Carrying Value']*3/100) + (df['Aerial Value']*9/100)).round(2).rank(pct=True))*99)).astype(int)
    df['No-Nonsense CB'] = (((((df['Minutes Normalized']*20/100) + (df['Ball Winning Value']*27/100) + (df['Sweeping Value']*29/100) + (df['Passing Value']*2/100) + (df['Possession Value']*3/100) + (df['Carrying Value']*1/100) + (df['Aerial Value']*18/100)).round(2).rank(pct=True))*99)).astype(int)
    df['Wide CB'] = (((((df['Minutes Normalized']*20/100) + (df['Ball Winning Value']*22/100) + (df['Sweeping Value']*7/100) + (df['Passing Value']*8/100) + (df['Possession Value']*2/100) + (df['Carrying Value']*32/100) + (df['Aerial Value']*9/100)).round(2).rank(pct=True))*99)).astype(int)

    return df

def FB_Rating(df):
    df['Ball Winning Value'] = (df['True Tackles Win Rate']*45/100) + (df['Interceptions per Oppo Touch']*30/100) + (df['True Tackles per Oppo Touch']*25/100) 
    df['Ball Winning Rank'] = (((df['Ball Winning Value'].rank(pct=True))*99)).astype(int)

    df['Sweeping Value'] = (df['Blocks per Oppo Touch']*35/100) + (df['Successful Defensive Aerials']*25/100) + (df['Clearances per Oppo Touch']*40/100)
    df['Sweeping Rank'] = (((df['Sweeping Value'].rank(pct=True))*99)).astype(int)

    df['Carrying Value'] = (df['Wide Progressive Carries per Touch']*30/100) + (df['Successful Dribbles per Touch']*40/100) + (df['Chance Creating Carries per Touch']*30/100)
    df['Carrying Rank'] = (((df['Carrying Value'].rank(pct=True))*99)).astype(int)

    df['Passing Value'] = (df['Normalized Progressive Passes']*30/100) + (df['Normalized Crosses']*25/100) + (df['Outward Distribution Rate']*45/100)
    df['Passing Rank'] = (((df['Passing Value'].rank(pct=True))*99)).astype(int)

    df['Creation Value'] = (df['Cutbacks']*45/100) + (df['Normalized Expected Assists']*30/100) + (df['Shot-Creating Actions']*25/100)
    df['Creation Rank'] = (((df['Creation Value'].rank(pct=True))*99)).astype(int)

    df['Possession Value'] = (df['Central Passes Received Rate']*50/100) + (df['Post-Recovery Passes']*25/100) + (df['Carries Inwards per Touch']*25/100)
    df['Possession Rank'] = (((df['Possession Value'].rank(pct=True))*99)).astype(int)

    df['Minutes Normalized'] = (((df['Minutes Normalized'].rank(pct=True))*99)).astype(int)

    #Full-Back Ratings
    df['Defensive FB'] = (((((df['Minutes Normalized']*20/100) + (df['Ball Winning Value']*30/100) + (df['Sweeping Value']*26/100) + (df['Passing Value']*5/100) + (df['Possession Value']*5/100) + (df['Carrying Value']*10/100) + (df['Creation Value']*3/100)).round(2).rank(pct=True))*99)).astype(int)
    df['Complete WB'] = (((((df['Minutes Normalized']*20/100) + (df['Ball Winning Value']*8/100) + (df['Sweeping Value']*4/100) + (df['Passing Value']*10/100) + (df['Possession Value']*7/100) + (df['Carrying Value']*25/100) + (df['Creation Value']*26/100)).round(2).rank(pct=True))*99)).astype(int)
    df['Inverted FB'] = (((((df['Minutes Normalized']*20/100) + (df['Ball Winning Value']*14/100) + (df['Sweeping Value']*5/100) + (df['Passing Value']*20/100) + (df['Possession Value']*30/100) + (df['Carrying Value']*1/100) + (df['Creation Value']*10/100)).round(2).rank(pct=True))*99)).astype(int)

    return df

def CM_Rating(df):
    df['Ball Winning Value'] = (df['True Tackles Win Rate']*30/100) + (df['Interceptions per Oppo Touch']*35/100) + (df['True Tackles per Oppo Touch']*35/100) 
    df['Ball Winning Rank'] = (((df['Ball Winning Value'].rank(pct=True))*99)).astype(int)

    df['Sweeping Value'] = (df['Blocks per Oppo Touch']*25/100) + (df['Successful Defensive Aerials']*45/100) + (df['Clearances per Oppo Touch']*30/100)
    df['Sweeping Rank'] = (((df['Sweeping Value'].rank(pct=True))*99)).astype(int)

    df['Carrying Value'] = (df['Central Progressive Carries per Touch']*40/100) + (df['Successful Dribbles per Touch']*25/100) + (df['Chance Creating Carries per Touch']*35/100)
    df['Carrying Rank'] = (((df['Carrying Value'].rank(pct=True))*99)).astype(int)

    df['Passing Value'] = (df['Normalized Central Progressive Passes']*35/100) + (df['Pass Completion %']*35/100) + (df['Normalized Completed Passes']*30/100)
    df['Passing Rank'] = (((df['Passing Value'].rank(pct=True))*99)).astype(int)

    df['Receiving Value'] = (df['Normalized Progressive Passes Received']*40/100) + (df['Half-Space Passes Received Rate']*40/100) + (df['Zone 14 Passes Received Rate']*20/100)
    df['Receiving Rank'] = (((df['Receiving Value'].rank(pct=True))*99)).astype(int)

    df['Possession Value'] = (df['Central Passes Received Rate']*35/100) + (df['Post-Recovery Passes']*30/100) + (df['Defensive Third Touches Rate']*35/100)
    df['Possession Rank'] = (((df['Possession Value'].rank(pct=True))*99)).astype(int)

    df['Minutes Normalized'] = (((df['Minutes Normalized'].rank(pct=True))*99)).astype(int)
    
    #Central Midfielder Ratings
    df['Ball-Winning (No.4)'] = (((((df['Minutes Normalized']*20/100) + (df['Ball Winning Value']*29/100) + (df['Sweeping Value']*26/100) + (df['Passing Value']*10/100) + (df['Possession Value']*13/100) + (df['Carrying Value']*1/100) + (df['Receiving Value']*1/100)).round(2)).rank(pct=True))*99).astype(int)
    df['Deep Lying (No.6)'] = (((((df['Minutes Normalized']*20/100) + (df['Ball Winning Value']*4/100) + (df['Sweeping Value']*9/100) + (df['Passing Value']*25/100) + (df['Possession Value']*35/100) + (df['Carrying Value']*6/100) + (df['Receiving Value']*1/100)).round(2)).rank(pct=True))*99).astype(int)
    df['Box-to-Box (No.8)'] = (((((df['Minutes Normalized']*20/100) + (df['Ball Winning Value']*15/100) + (df['Sweeping Value']*2/100) + (df['Passing Value']*12/100) + (df['Possession Value']*11/100) + (df['Carrying Value']*22/100) + (df['Receiving Value']*18/100)).round(2)).rank(pct=True))*99).astype(int)
    
    return df

def AM_Rating(df):
    df['Ball Winning Value'] = (df['True Tackles per Oppo Touch']*35/100) + (df['True Interceptions per Oppo Touch']*25/100) + (df['Att 3rd Tackles per Oppo Def 3rd Touch']*40/100) 
    df['Ball Winning Rank'] = (((df['Ball Winning Value'].rank(pct=True))*99)).astype(int)

    df['Carrying Value'] = (df['Progressive Carries per Touch']*35/100) + (df['Successful Dribbles per Touch']*30/100) + (df['Chance Creating Carries per Touch']*35/100)
    df['Carrying Rank'] = (((df['Carrying Value'].rank(pct=True))*99)).astype(int)

    df['Receiving Value'] = (df['Normalized Progressive Passes Received']*30/100) + (df['Half-Space Passes Received Rate']*30/100) + (df['Zone 14 Passes Received Rate']*40/100)
    df['Receiving Rank'] = (((df['Receiving Value'].rank(pct=True))*99)).astype(int)

    df['Passing Value'] = (df['Normalized Progressive Passes']*40/100) + (df['Normalized Half Space Passes']*35/100) + (df['Outward Distribution Rate']*25/100)
    df['Passing Rank'] = (((df['Passing Value'].rank(pct=True))*99)).astype(int)

    df['Shooting Value'] = (df['npxG per Shot']*45/100) + (df['NpG-xG']*30/100) + (df['Shots on Target %']*25/100)
    df['Shooting Rank'] = (((df['Shooting Value'].rank(pct=True))*99)).astype(int)

    df['Creation Value'] = (df['Normalized Expected Assists']*30/100) + (df['Normalized Key Passes']*35/100) + (df['Shot-Creating Actions']*35/100)
    df['Creation Rank'] = (((df['Creation Value'].rank(pct=True))*99)).astype(int)

    df['Minutes Normalized'] = (((df['Minutes Normalized'].rank(pct=True))*99)).astype(int)
    
    #Attacking Midfielder Ratings
    df['Half Winger'] = (((((df['Minutes Normalized']*20/100) + (df['Ball Winning Value']*15/100) + (df['Carrying Value']*23/100) + (df['Receiving Value']*26/100) + (df['Passing Value']*8/100) + (df['Creation Value']*5/100) + (df['Shooting Value']*3/100)).round(2)).rank(pct=True))*99).astype(int)
    df['Advanced Creator'] = (((((df['Minutes Normalized']*20/100) + (df['Ball Winning Value']*5/100) + (df['Carrying Value']*5/100) + (df['Receiving Value']*17/100) + (df['Passing Value']*24/100) + (df['Creation Value']*25/100) + (df['Shooting Value']*4/100)).round(2)).rank(pct=True))*99).astype(int)
    df['Second Striker'] = (((((df['Minutes Normalized']*20/100) + (df['Ball Winning Value']*4/100) + (df['Carrying Value']*6/100) + (df['Receiving Value']*27/100) + (df['Passing Value']*5/100) + (df['Creation Value']*10/100) + (df['Shooting Value']*28/100)).round(2)).rank(pct=True))*99).astype(int)
    
    return df

def W_Rating(df):
    df['Ball Winning Value'] = (df['True Tackles per Oppo Touch']*40/100) + (df['True Interceptions per Oppo Touch']*25/100) + (df['Att 3rd Tackles per Oppo Def 3rd Touch']*35/100) 
    df['Ball Winning Rank'] = (((df['Ball Winning Value'].rank(pct=True))*99)).astype(int)

    df['Carrying Value'] = (df['Wide Progressive Carries per Touch']*35/100) + (df['Successful Dribbles per Touch']*35/100) + (df['Carries Inwards per Touch']*30/100)
    df['Carrying Rank'] = (((df['Carrying Value'].rank(pct=True))*99)).astype(int)

    df['Passing Value'] = (df['Normalized Central Progressive Passes']*35/100) + (df['Normalized Half Space Passes']*35/100) + (df['Outward Distribution Rate']*30/100)
    df['Passing Rank'] = (((df['Passing Value'].rank(pct=True))*99)).astype(int)

    df['Receiving Value'] = (df['Normalized Progressive Passes Received']*30/100) + (df['Wide Passes Received Rate']*35/100) + (df['Normalized Att Pen Touches']*35/100)
    df['Receiving Rank'] = (((df['Receiving Value'].rank(pct=True))*99)).astype(int)

    df['Creation Value'] = (df['Normalized Expected Assists']*30/100) + (df['Normalized Key Passes']*35/100) + (df['Shot-Creating Actions']*35/100)
    df['Creation Rank'] = (((df['Creation Value'].rank(pct=True))*99)).astype(int)

    df['Shooting Value'] = (df['npxG per Shot']*35/100) + (df['NpG-xG']*35/100) + (df['Shot-Ending Carries per Touch']*30/100)
    df['Shooting Rank'] = (((df['Shooting Value'].rank(pct=True))*99)).astype(int)

    df['Minutes Normalized'] = (((df['Minutes Normalized'].rank(pct=True))*99)).astype(int)
    
    #Winger Ratings
    df['Direct Winger'] = (((((df['Minutes Normalized']*20/100) + (df['Ball Winning Value']*18/100) + (df['Carrying Value']*29/100) + (df['Receiving Value']*13/100) + (df['Passing Value']*3/100) + (df['Creation Value']*14/100) + (df['Shooting Value']*3/100)).round(2)).rank(pct=True))*99).astype(int)
    df['Wide Playmaker'] = (((((df['Minutes Normalized']*20/100) + (df['Ball Winning Value']*3/100) + (df['Carrying Value']*4/100) + (df['Receiving Value']*15/100) + (df['Passing Value']*27/100) + (df['Creation Value']*28/100) + (df['Shooting Value']*3/100)).round(2)).rank(pct=True))*99).astype(int)
    df['Inside Forward'] = (((((df['Minutes Normalized']*20/100) + (df['Ball Winning Value']*3/100) + (df['Carrying Value']*14/100) + (df['Receiving Value']*25/100) + (df['Passing Value']*3/100) + (df['Creation Value']*5/100) + (df['Shooting Value']*30/100)).round(2)).rank(pct=True))*99).astype(int)
    
    return df
    
def CF_Rating(df):
    df['Ball Winning Value'] = (df['True Tackles per Oppo Touch']*35/100) + (df['True Interceptions per Oppo Touch']*25/100) + (df['Att 3rd Tackles per Oppo Def 3rd Touch']*40/100) 
    df['Ball Winning Rank'] = (((df['Ball Winning Value'].rank(pct=True))*99)).astype(int)

    df['Carrying Value'] = (df['Progressive Carries per Touch']*35/100) + (df['Successful Dribbles per Touch']*25/100) + (df['Chance Creating Carries per Touch']*40/100)
    df['Carrying Rank'] = (((df['Carrying Value'].rank(pct=True))*99)).astype(int)

    df['Passing Value'] = (df['Normalized Progressive Passes']*30/100) + (df['Normalized Completed Passes']*40/100) + (df['Normalized Half Space Passes']*30/100)
    df['Passing Rank'] = (((df['Passing Value'].rank(pct=True))*99)).astype(int)

    df['Receiving Value'] = (df['Normalized Progressive Passes Received']*40/100) + (df['Wide Passes Received Rate']*20/100) + (df['Normalized Att Pen Touches']*40/100)
    df['Receiving Rank'] = (((df['Receiving Value'].rank(pct=True))*99)).astype(int)

    df['Aerial Value'] = (df['Aerial Duels Won %']*15/100) + (df['Successful Offensive Aerials']*85/100)
    df['Aerial Rank'] = (((df['Aerial Value'].rank(pct=True))*99)).astype(int)

    df['Shooting Value'] = (df['npxG per Shot']*40/100) + (df['NpG-xG']*40/100) + (df['Shots on Target %']*20/100)
    df['Shooting Rank'] = (((df['Shooting Value'].rank(pct=True))*99)).astype(int)

    df['Minutes Normalized'] = (((df['Minutes Normalized'].rank(pct=True))*99)).astype(int)
    
    #Centre-Forward Ratings
    df['Advanced Forward'] = (((((df['Minutes Normalized']*20/100) + (df['Ball Winning Value']*1/100) + (df['Carrying Value']*11/100) + (df['Receiving Value']*21/100) + (df['Passing Value']*1/100) + (df['Aerial Value']*15/100) + (df['Shooting Value']*31/100)).round(2)).rank(pct=True))*99).astype(int)
    df['Pressing Forward'] = (((((df['Minutes Normalized']*20/100) + (df['Ball Winning Value']*35/100) + (df['Carrying Value']*5/100) + (df['Receiving Value']*2/100) + (df['Passing Value']*15/100) + (df['Aerial Value']*14/100) + (df['Shooting Value']*9/100)).round(2)).rank(pct=True))*99).astype(int)
    df['Target Forward'] = (((((df['Minutes Normalized']*20/100) + (df['Ball Winning Value']*2/100) + (df['Carrying Value']*3/100) + (df['Receiving Value']*6/100) + (df['Passing Value']*17/100) + (df['Aerial Value']*32/100) + (df['Shooting Value']*20/100)).round(2)).rank(pct=True))*99).astype(int)
    
    return df   

#######################################################################

if not df.empty and 'Position' in df.columns and len(df['Position']) > 0:
    if df['Position'].iloc[0] == 'Centre-Back':
        df = CB_Rating(df)
        df = pd.merge(df, age, on="Player")
        df.rename(columns = {'Minutes Played_y':'Minutes Played'},inplace = True)
        
        df = df[['Player','True Position','Position','Age','Squad','League','Minutes Played','Ball Winning Rank','Sweeping Rank','Possession Rank','Passing Rank','Carrying Rank','Aerial Rank','Ball-Playing CB','No-Nonsense CB','Wide CB']]

    if df['Position'].iloc[0] == 'Full-Back':
        df = FB_Rating(df)
        df = pd.merge(df, age, on="Player")
        df.rename(columns = {'Minutes Played_y':'Minutes Played'},inplace = True)
        df = df[['Player','True Position','Position','Age','Squad','League','Minutes Played','Ball Winning Rank','Sweeping Rank','Possession Rank','Passing Rank','Carrying Rank','Creation Rank','Defensive FB', 'Complete WB', 'Inverted FB']]
        
    if df['Position'].iloc[0] == 'Central Midfielder':
        df = CM_Rating(df)
        df = pd.merge(df, age, on="Player")
        df.rename(columns = {'Minutes Played_y':'Minutes Played'},inplace = True)
        df = df[['Player','True Position','Position','Age','Squad','League','Minutes Played','Ball Winning Rank','Sweeping Rank','Possession Rank','Passing Rank','Carrying Rank','Receiving Rank','Ball-Winning (No.4)','Deep Lying (No.6)','Box-to-Box (No.8)']]
        
    if df['Position'].iloc[0] == 'Attacking Midfielder':
        df = AM_Rating(df)
        df = pd.merge(df, age, on="Player")
        df.rename(columns = {'Minutes Played_y':'Minutes Played'},inplace = True)
        df = df[['Player','True Position','Position','Age','Squad','League','Minutes Played','Ball Winning Rank','Carrying Rank','Creation Rank','Passing Rank','Receiving Rank','Shooting Rank','Half Winger','Advanced Creator','Second Striker']]

    if df['Position'].iloc[0] == 'Winger':
        df = W_Rating(df)
        df = pd.merge(df, age, on="Player")
        df.rename(columns = {'Minutes Played_y':'Minutes Played'},inplace = True)
        df = df[['Player','True Position','Position','Age','Squad','League','Minutes Played','Ball Winning Rank','Carrying Rank','Passing Rank','Creation Rank','Receiving Rank','Shooting Rank','Direct Winger','Wide Playmaker','Inside Forward']]

    if df['Position'].iloc[0] == 'Centre-Forward':
        df = CF_Rating(df)
        df = pd.merge(df, age, on="Player")
        df.rename(columns = {'Minutes Played_y':'Minutes Played'},inplace = True)
        df = df[['Player','True Position','Position','Age','Squad','League','Minutes Played','Ball Winning Rank','Passing Rank','Carrying Rank','Receiving Rank','Shooting Rank','Aerial Rank','Advanced Forward','Pressing Forward','Target Forward']]
            
#######################################################################
sdf = df[['Player','True Position','Age','Squad','League'] + list(df.columns[7:13])]

# Normalize the data using z-score scaling (standardization)
scaler = StandardScaler()
normalized_data = scaler.fit_transform(sdf[sdf.columns[7:]])

# Apply K-means clustering
num_clusters = 5 # You can choose the number of clusters based on your requirements
#kmeans = KMeans(n_clusters=num_clusters, n_init='auto', random_state=42)
kmeans = KMeans(n_clusters=num_clusters, n_init='auto')
clusters = kmeans.fit_predict(normalized_data)

# Add cluster labels to the DataFrame
sdf['Cluster'] = clusters

# Find the cluster of the selected player
selected_player_cluster = sdf.loc[sdf['Player'] == player, 'Cluster'].values[0]

# Get players in the same cluster as the selected player
similar_players = sdf[sdf['Cluster'] == selected_player_cluster]

# Check if the selected player exists in the cluster
if player in similar_players['Player'].values:
    
    # Extract the selected player's stats
    selected_player_stats = similar_players[similar_players['Player'] == player].iloc[0, 5:-1].values.astype(float)

 # Calculate the Euclidean distance of each player in the cluster from the selected player
    distances = np.linalg.norm(similar_players[similar_players.columns[5:-1]].values - selected_player_stats, axis=1)

    # Add the 'Distance' column to the DataFrame
    similar_players['Distance'] = distances

    # Sort the players by distance (similarity) and select the top 5 most similar players
    top_7_indices = distances.argsort()[1:8]  # Exclude the selected player itself
    top_7_similar_players = similar_players.iloc[top_7_indices]

top_7_similar_players = top_7_similar_players.iloc[:, :5].reset_index(drop=True)
top_7_similar_players = pd.merge(top_7_similar_players, age, on="Player")

top_7_similar_players = top_7_similar_players[['Player','Age_y','True Position','Squad','League','Minutes Played']]
top_7_similar_players.rename(columns = {'Age_y':'Age', 'True Position':'Main Position'},inplace = True)
top_7_similar_players.index += 1
Most_Similar = top_7_similar_players['Player'].values[0]
Age = top_7_similar_players['Age'].values[0]

#######################################################################

#Filter for player
df = df.loc[(df['Player'] == player)].reset_index(drop= True)

#add ranges to list of tuple pairs
values = []

for x in range(len(df['Player'])):
    if df['Player'][x] == player:
        values = df.iloc[x].values.tolist()
        

position = values[2]
age = values[3]
team = values[4]
minutes = values[6]
score1 = values[-3] 
score2 = values[-2]  
score3 = values[-1]  
values = values[7:13]

#get parameters
params = list(df.columns)
params = params[7:13]
params = [y[:-5] for y in params]

#get roles
roles = list(df.columns)
roles = roles[-3:]

#######################################################################

# color for the slices and text
slice_colors = ["#42b84a"] * 2 + ["#fbcf00"] * 2 + ["#39a7ab"] * 2
text_colors = ["#000000"] * 2 +  ["#000000"] * 2 + ["#000000"] * 2

# instantiate PyPizza class
baker = PyPizza(
    params=params,                    
    background_color="#f1e9d2",        
    straight_line_color="#000000",    
    straight_line_lw=2,               
    last_circle_color="black",      
    last_circle_lw= 5,                
    other_circle_lw=2,                
    inner_circle_size=0               
)

# plot pizza
fig, ax = baker.make_pizza(
    values,                          
    figsize=(8,10),                 
    color_blank_space="same",        
    slice_colors=slice_colors,       
    value_colors=text_colors,        
    value_bck_colors=slice_colors,   
    blank_alpha=0.4,                 
    kwargs_slices=dict(
        edgecolor="black", zorder=3, linewidth=4
    ),                              
    kwargs_params=dict(
        color="black", fontsize=17,fontfamily='DejaVu Sans',  va="center"
    ),                               
    kwargs_values=dict(
        color="black", fontsize=20,fontweight='bold',
         zorder=3,
        bbox=dict(
            edgecolor="black", facecolor="#FFFFFF",
            boxstyle="round,pad=0.2", lw=2.5
        )
    )                                
)


# add text
fig.text(
    1.4, 1.04, "Space",size=10, ha="center", fontweight='bold', color="none"
)

# add text
fig.text(
    1.4, 0.09, "Space",size=10, ha="center", fontweight='bold', color="none"
)

# add text
fig.text(
    0.095, 1, "Space",size=10, ha="center", fontweight='bold',color="none"
)

# add text
fig.text(
    0.75, 1.01, player + ", " + str(age) + " - " + team,size=32,
    ha="center", fontweight='bold',  color="black"
)

# add text
fig.text(
    0.75, 0.96, position + " Template | "+ str(minutes) + " Minutes Played",size=23,
    ha="center",  color="black"
)


# add text
fig.text(
    0.75, 0.91, "Most Similar Player: " + Most_Similar + ", "+ str(Age) ,size=20,
    ha="center", color="black"
)


fig.text(
    1.14, 0.78, score1, size=50,
    ha="left", fontweight='bold', color="black",
    bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3', lw=3)
)

# add text
fig.text(
    1.2, 0.68, roles[0] + "\nPercentile Rank" ,size=19,
    ha="center", fontweight='bold', color="black"
)

fig.text(
    1.14, 0.516, score2, size=50,
    ha="left", fontweight='bold', color="black",
    bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3', lw=3)
)

# add text
fig.text(
    1.2, 0.417, roles[1] + "\nPercentile Rank" ,size=19,
    ha="center", fontweight='bold', color="black"
)

fig.text(
    1.14, 0.267, score3, size=50,
    ha="left", fontweight='bold', color="black",
    bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3', lw=3)
)

# add text
fig.text(
    1.2, 0.166, roles[2] +"\nPercentile Rank" ,size=19,
    ha="center", fontweight='bold', color="black"
)

# add text
fig.text(
    0.75, 0.1, "Note: Top 7 European Leagues Players with 1080+ Minutes Included | Data: Opta | By @chunhang7" ,
    size=15, ha="center", color="black"
)

# Display the plot
st.pyplot(fig)

st.markdown('<p style="font-weight:bold; font-size: 20px; color: #808080;">Similar Players to ' + player + ' (' + position + ' Template)', unsafe_allow_html=True)
st.dataframe(top_7_similar_players)

with st.expander("What's Next"):
    st.write('''
    -> Comparing Feature\n
    -> Goalkeeper Ranking System
    ''')

with st.expander("Special Thanks"):
    st.write('''
    Player Ratings was originally inspired by Scott Willis (@scottjwillis), Liam Henshaw (@HenshawAnalysis) & Andy Watson (@andywatsonsport).\n
    Ben Griffis (@BeGriffis) was kind enough to share his previous work for me to draw Inspiration.\n
    Joel A. Adejola (@joeladejola), Anuraag Kulkarni (@Anuraag027) , Rahul (@exceedingxpuns), Yusuf Raihan (@myusufraihan) & Daryl Dao (@dgouilard) for their thought-provoking review on the metrics applied here.\n
    Thank you for the support!
    ''')
