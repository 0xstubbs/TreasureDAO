import streamlit as st
import pandas as pd
import altair as alt
from datetime import date
import numpy as np
import os
# from dotenv import load_dotenv
import boto3

import sys
sys.path.append('./modules/')
# import thegraph


# load_dotenv()

try:
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    # AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    # AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    client = boto3.client('s3', aws_access_key_id = AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
except:
    AWS_ACCESS_KEY_ID = st.secrets['AWS_ACCESS_KEY_ID']
    AWS_SECRET_ACCESS_KEY = st.secrets['AWS_SECRET_ACCESS_KEY']
    client = boto3.client('s3', aws_access_key_id = AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)


st.set_page_config(layout='wide')
pd.set_option('display.precision', 2)
st.image('https://skycatcher.xyz/images/logo-white.svg')
header = st.container()
dataset = st.container()
legion_tokens = st.container()

st.sidebar.markdown("### Treasure Ecosystem Overview")
st.sidebar.markdown("This app will go over the basics of the Treasure Ecosystem.")
st.sidebar.markdown("Link to BridgeWorld: [BridgeWorld](https://bridgeworld.treasure.lol/)")
st.sidebar.markdown("Link to Trove Marketplace: [Trove](https://trove.treasure.lol/)")

with header:
    st.title('Treasure Ecosystem')
    

#----------------------------------------------#
#Page Layout
#The page will be 3 columns (column 1: sidebar, column 2, column3)
col1 = st.sidebar
col2, col3 = st.columns((2,1))    

tab1, tab2, tab3 = st.tabs(['Magic Token', 'Legion', 'Trove'])

expander_test = st.expander
#---------------------------------------------#

    
s3_bucket = "stubbs-file-storage-streamlit"
region = "us-west-1"

@st.experimental_memo(ttl=1200)
def load_supply_over_time():
    file_name = 'supply_over_time.csv'
    obj=client.get_object(Bucket=s3_bucket, Key=file_name)
    df = pd.read_csv(obj['Body'])
    return df

def load_excluded_addresses():
    
    file_name = 'excluded_addresses.csv'
    obj=client.get_object(Bucket=s3_bucket, Key=file_name)
    df = pd.read_csv(obj['Body'])
    return df

def load_balances_by_day():
    file_name = 'balances_by_day.csv'
    obj=client.get_object(Bucket=s3_bucket, Key=file_name)
    df = pd.read_csv(obj['Body'])
    
    return df  

def load_legion_nft_holders_over_time():
    file_name = 'legion_holders_by_day.csv'
    obj=client.get_object(Bucket=s3_bucket, Key=file_name)
    df = pd.read_csv(obj['Body'])
    
    return df

def unique_legion_holders():
    file_name = 'unique_legion_holders.csv'
    obj=client.get_object(Bucket=s3_bucket, Key=file_name)
    df = pd.read_csv(obj['Body'])
    return df

minted_over_time = load_supply_over_time()
minted_over_time['amount'] = minted_over_time['amount'].apply(lambda x: -1*x)
minted_over_time['cumsum'] = minted_over_time['cumsum'].apply(lambda x: -1 * x)

with tab1:
    st.header('$MAGIC Token')
    tab1_col1, tab1_col2 = st.columns((1,2))
    st.header('Current Wallet Balances')
    tab1_col1_2, tab1_col2_2 = st.columns((1,1))


with tab1_col1:
    total_magic_supply = abs(minted_over_time['cumsum'].iloc[-1])
    st.metric('Total MAGIC Supply', "{:,.0f}".format(total_magic_supply))



    # st.line_chart(minted_over_time, x='date', y=['cumsum', 'amount'])
    
with tab1_col2:
    st.header('Magic Supply Growth')
    chart = alt.Chart(minted_over_time).mark_area().encode(
        x = 'date:T',
        y='cumsum:Q',
        tooltip = ['date:T', 'amount:Q', 'cumsum:Q']
    )
    st.altair_chart(chart, use_container_width=True)
    
with tab1_col1_2:
    
    balances = load_balances_by_day()
    balances.drop(balances.columns[0], axis=1, inplace=True)
    balances['date'] = pd.to_datetime(balances['date']).dt.date
    balances = balances.sort_values('cumsum', ascending=False)
    balances_today = balances[balances['date'] == balances['date'].max()][['date','wallet_address','cumsum']]
    
    df_excluded_addresses = load_excluded_addresses()[['Name', 'Wallet Address']]
    excluded_addresses = df_excluded_addresses['Wallet Address'].str.lower().to_list()
    
    balances_today_wo_contracts = balances_today[~balances_today['wallet_address'].isin(excluded_addresses)]
    balances_excluded = balances_today[balances_today['wallet_address'].isin(excluded_addresses)]
    st.write('Wallet Balances <not staking contracts>')
    st.dataframe(balances_today_wo_contracts, width=1400, height=600)

with tab1_col2_2:
    excluded_address_expander = st.expander('Excluded Addresses')
    st.write('Wallet Balances <Staking Contract, LP, etc>')
    balances_excluded = balances_excluded.merge(df_excluded_addresses, how='left', left_on='wallet_address', right_on='Wallet Address')
    balances_excluded = balances_excluded[['date', 'Name', 'cumsum','Wallet Address']]
    st.dataframe(balances_excluded, width=1400, height=600)
    
with excluded_address_expander:
    st.write('Staking contracts, DAO Multisigs, and Markets are excluded')
    st.dataframe(df_excluded_addresses)

#----------------------------------------------------------------------------------------------------------------------------#
#Add section where the user can input a specific wallet address and get stats back.
with tab1:
    st.header('Individual Stats')
    
    wallet_address = st.text_input('Input wallet wallet address: ', value='0xa0a89db1c899c49f98e6326b764bafcf167fc2ce', placeholder='0xa0a89db1c899c49f98e6326b764bafcf167fc2ce')
    col1_indiv_stats, col2_indiv_stats = st.columns((1,1))
    specific_balances = balances[balances['wallet_address']== wallet_address.casefold()]   #[['date', 'cumsum']]
    specific_balances = specific_balances.sort_values(by='date', ascending=False)
    
with col1_indiv_stats:
    st.dataframe(specific_balances[['date', 'wallet_address', 'cumsum']])
    
with col2_indiv_stats:
    st.write('Wallet Balance over Time')
    wallet_bal_chart = chart = alt.Chart(specific_balances).mark_area().encode(
        x = 'date:T',
        y='cumsum:Q',
        # size = 'amount:Q',
        tooltip = ['date:T', 'cumsum:Q']
    )
    st.altair_chart(wallet_bal_chart, use_container_width=True)
    
with tab2:
    
    df_legion_holders_by_day = load_legion_nft_holders_over_time()
    df_legion_holders_by_day_total = df_legion_holders_by_day[df_legion_holders_by_day['address']!='0x0000000000000000000000000000000000000000']
    df_legion_holders_by_day_total = (df_legion_holders_by_day_total[['date','cumsum']]).groupby('date')['cumsum'].sum().reset_index()
    
    
    
    # df=df_legion_holders_by_day_total.groupby(['date'])['cumsum'].sum().reset_index()
    df_legion_holders_by_day = df_legion_holders_by_day[df_legion_holders_by_day['cumsum']>0].sort_values('date', ascending=False).drop(columns={'Unnamed: 0'})
    df_unique_legion_holders = unique_legion_holders()
    
    st.header('NFT Stats')   
    st.metric('Number of Legion NFTs', df_legion_holders_by_day_total['cumsum'].iloc[-1])
    col1_nft_stats, col2_nft_stats = st.columns((2,1))

    st.write('Number of Unique Holders over Time')
    unique_legion_chart = chart = alt.Chart(df_unique_legion_holders).mark_area().encode(
        x = 'date:T',
        y='unique_holders:Q',
        # color='wallet_address:N',
        # size = 'amount:Q',
        tooltip = ['date:T', 'unique_holders:Q']
    )
    st.altair_chart(unique_legion_chart, use_container_width=True)
with col1_nft_stats:
    st.write('Number of Legion NFT over Time')
    legion_chart = alt.Chart(df_legion_holders_by_day_total).mark_area().encode(
    x = 'date:T',
    y='cumsum:Q',
    # color='wallet_address:N',
    # size = 'amount:Q',
    tooltip = ['date:T', 'cumsum:Q']
    )
    st.altair_chart(legion_chart, use_container_width=True)

with col2_nft_stats:
    st.dataframe(df_legion_holders_by_day, width=1400, height=600)    
    
with tab3:
    st.header('Trove Marketplace')
    collections = thegraph.get_collections()
    
    option = st.selectbox(
     'Select Collection...',
     collections)

    st.write('You selected:', option)