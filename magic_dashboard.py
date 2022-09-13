import streamlit as st
import plotly.express as px
import pandas as pd
import altair as alt
from datetime import date
import numpy as np
import os
import io
# from dotenv import load_dotenv
import boto3
import requests

import sys
sys.path.append('./modules/')
# import thegraph

# load_dotenv()

#---------------------------------------------------------------------------------------------------------------------------#
#Use a try/except clause to get the environment variables for access to AWS S3 bucket whether running locally or in streamlit app
try:
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

except:
    AWS_ACCESS_KEY_ID = st.secrets['AWS_ACCESS_KEY_ID']
    AWS_SECRET_ACCESS_KEY = st.secrets['AWS_SECRET_ACCESS_KEY']

# client = boto3.client('s3', aws_access_key_id = AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
client = boto3.resource('s3', aws_access_key_id = AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
s3_bucket = "stubbs-file-storage-streamlit"
region = "us-west-1"

# @st.experimental_memo(ttl=1200)
# def load_supply_over_time():
#     file_name = 'supply_over_time.csv'
#     obj=client.get_object(Bucket=s3_bucket, Key=file_name)
#     df = pd.read_csv(obj['Body'])
#     return df

# @st.experimental_memo(ttl=1200)
# def load_excluded_addresses():
    
#     file_name = 'excluded_addresses.csv'
#     obj=client.get_object(Bucket=s3_bucket, Key=file_name)
#     df = pd.read_csv(obj['Body'])
#     return df

# @st.experimental_memo(ttl=1200)
# def load_balances_by_day():
#     file_name = 'balances_by_day.csv'
#     obj=client.get_object(Bucket=s3_bucket, Key=file_name)
#     df = pd.read_csv(obj['Body'])
    
#     return df  
@st.experimental_memo(ttl=1200)
def load_balances_by_day_parquet():
    buffer=io.BytesIO()
    s3_bucket = "stubbs-file-storage-streamlit"
    file_name = 'balances_by_day.parquet'
    
    obj=client.Object(s3_bucket, file_name)
    obj.download_fileobj(buffer)
    df = pd.read_parquet(buffer, engine='pyarrow')
    
    return df  

# @st.experimental_memo(ttl=1200)
# def load_legion_nft_holders_over_time():
#     file_name = 'legion_holders_by_day.csv'
#     obj=client.get_object(Bucket=s3_bucket, Key=file_name)
#     df = pd.read_csv(obj['Body'])
    
#     return df

# @st.experimental_memo(ttl=1200)
# def unique_legion_holders():
#     file_name = 'unique_legion_holders.csv'
#     obj=client.get_object(Bucket=s3_bucket, Key=file_name)
#     df = pd.read_csv(obj['Body'])
#     return df

# minted_over_time = load_supply_over_time()
# minted_over_time['amount'] = minted_over_time['amount'].apply(lambda x: -1*x)
# minted_over_time['cumsum'] = minted_over_time['cumsum'].apply(lambda x: -1 * x)




#---------------------------------------------------------------------------------------------------------------------------#
#Start creating layout for app
st.set_page_config(layout='wide')
pd.set_option('display.precision', 2)
st.image('https://skycatcher.xyz/images/logo-white.svg')
header = st.container()
# dataset = st.container()
# legion_tokens = st.container()

#---------------------------------------------------------------------------------------------------------------------------#
#Create a sidebar with links to important sites
st.sidebar.markdown("### Treasure Ecosystem Overview")
st.sidebar.markdown("This app will go over the basics of the Treasure Ecosystem.")
st.sidebar.markdown("Link to BridgeWorld: [BridgeWorld](https://bridgeworld.treasure.lol/)")
st.sidebar.markdown("Link to Trove Marketplace: [Trove](https://trove.treasure.lol/)")
#---------------------------------------------------------------------------------------------------------------------------#

with header:
    st.title('Treasure Ecosystem')
    

#----------------------------------------------#
#Page Layout
#The page will be 3 columns (column 1: sidebar, column 2, column3)
col1 = st.sidebar
col2, col3 = st.columns((2,1))    

tab1, tab2, tab3 = st.tabs(['Magic Token', 'NFTs', 'Trove'])



# expander_test = st.expander
# #---------------------------------------------#

    


with tab1:
    st.header('$MAGIC Token')
    
    #----------------------------------------------------------------------------------
    #-----------------Get CoinGecko Market Data on $MAGIC Token------------------------
    @st.experimental_memo(ttl=1200)
    def get_coingecko_market_data():
        url='https://api.coingecko.com/api/v3/coins/ethereum/contract/0xb0c7a3ba49c7a6eaba6cd4a96c55a1391070ac9a/market_chart/?vs_currency=usd&days=max'
        response=requests.get(url).json()
        
        #Get the Prices
        prices=response['prices']
        df_prices = pd.DataFrame(prices).rename(columns={0:'timestamp', 1:'price'})
        df_prices['datetime'] = pd.to_datetime(df_prices['timestamp'], unit='ms')
        df_prices=df_prices[['timestamp', 'datetime', 'price']]
        
        #Get marketcap data
        mc = response['market_caps']
        df_mc = pd.DataFrame(mc).rename(columns={0:'timestamp', 1:'marketcap'})
        df_mc['datetime']=pd.to_datetime(df_mc['timestamp'], unit='ms')
        df_mc=df_mc[['timestamp', 'datetime', 'marketcap']]
        df_mc=df_mc[df_mc['marketcap']>0]
        
        #Get total volume data
        total_vol = response['total_volumes']
        df_volume = pd.DataFrame(total_vol).rename(columns={0:'timestamp', 1:'total_volume'})
        df_volume['datetime'] = pd.to_datetime(df_volume['timestamp'], unit='ms')
        df_volume = df_volume[['timestamp', 'datetime', 'total_volume']]
        
        return df_prices, df_mc, df_volume
        
    cg_prices, cg_mc, cg_volume = get_coingecko_market_data()
    
    tab1_col1_cg, tab1_col2_cg, tab1_col3_cg = st.columns((1,1, 1))
    with tab1_col1_cg:
        current_price_df = cg_prices.sort_values('datetime', ascending=False)
        price_array = np.array(current_price_df['price'])
        current_price = price_array[0]
        # prev_price = 
        st.metric('Current Magic Price', value=f'${current_price:,.3f}')
    with tab1_col2_cg:
        current_mc_df = cg_mc.sort_values('datetime', ascending=False)
        mc_array = np.array(current_mc_df['marketcap'])
        current_mc = mc_array[0]
        # prev_price = 
        st.metric('Current Market Cap', value=f'${current_mc:,.0f}')
    with tab1_col3_cg:
        current_vol_df = cg_volume.sort_values('datetime', ascending=False)
        volume_array = np.array(current_vol_df['total_volume'])
        current_vol = volume_array[0]
        prev_volume = volume_array[1]
        change = (current_vol - prev_volume)/prev_volume
        st.metric('24h Volume', value=f'${current_vol:,.0f}', delta=f'{change:,.3f}%')
        
        
    chart_choice = st.radio(label='Select Chart', options=['Price', 'Marketcap', '24hr Volume'])
    if chart_choice == 'Price':
        df = current_price_df
        y_select = 'price'
        title_select = '$MAGIC Price'
        label_select ={'datetime':"Date", 'price': "MAGIC Price (USD)"}
    elif chart_choice == 'Marketcap':
        df = current_mc_df
        y_select = 'marketcap'
        title_select = 'Total MAGIC Marketcap'
        label_select ={'datetime':"Date", 'marketcap': "Total Marketcap (USD)"}
    elif chart_choice == '24hr Volume':
        df = current_vol_df
        y_select = 'total_volume'
        title_select = '24hr Trade Volume'
        label_select ={'datetime':"Date", 'total_volume': "24hr Trading Volume (USD)"}
    
    fig = px.area(df, x="datetime", y=y_select, title=title_select, labels = label_select)#, color=y_select)#, line_group="country")
    fig.update_layout(hovermode="x unified")
    # fig.show()
    
    st.plotly_chart(fig, use_container_width=True)
    st.write('Market Information: CoinGecko API')
    
#---------------------------------------------------------------------------------------------------------------------------------------------------#
#                                                                                                                                                   #
#                                              Token Distribution Section                                                                           #
#                                                                                                                                                   #
#---------------------------------------------------------------------------------------------------------------------------------------------------#
    
    df_wallet_balances = load_balances_by_day_parquet()
    daily_total = df_wallet_balances.groupby('date')['cumsum'].sum().reset_index()
    
    total_array = np.array(daily_total['cumsum'])
    total_array_lag=np.concatenate(([0], total_array[:-1]))
    daily_change = total_array-total_array_lag
    daily_total['change'] = daily_change
    
    tab1_col1, tab1_col2 = st.columns((1,2))
    st.header('Current Wallet Balances')
    
    tab1_col1_2, tab1_col2_2 = st.columns((1,1))
    
    with tab1_col1_2:
        current_supply = np.array(daily_total['cumsum'])[-1]
        st.metric(label="Current MAGIC Supply", value = f'{current_supply:,.0f}')
    with tab1_col2_2:
        change = np.array(daily_total['change'])[-1]
        st.metric(label="Change", value = f'{change:,.0f}')
    
    fig = px.area(daily_total, x="date", y='cumsum', title='MAGIC Supply')
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)
    

# with tab1_col1:
#     # total_magic_supply = abs(minted_over_time['cumsum'].iloc[-1])
#     st.metric('Total MAGIC Supply', "{:,.0f}".format(total_magic_supply))



#     # st.line_chart(minted_over_time, x='date', y=['cumsum', 'amount'])
    
# with tab1_col2:
#     st.header('Magic Supply Growth')
#     chart = alt.Chart(minted_over_time).mark_area().encode(
#         x = 'date:T',
#         y='cumsum:Q',
#         tooltip = ['date:T', 'amount:Q', 'cumsum:Q']
#     )
#     st.altair_chart(chart, use_container_width=True)
    
# with tab1_col1_2:
    
#     balances = load_balances_by_day()
#     balances.drop(balances.columns[0], axis=1, inplace=True)
#     balances['date'] = pd.to_datetime(balances['date']).dt.date
#     balances = balances.sort_values('cumsum', ascending=False)
#     balances_today = balances[balances['date'] == balances['date'].max()][['date','wallet_address','cumsum']]
    
#     df_excluded_addresses = load_excluded_addresses()[['Name', 'Wallet Address']]
#     excluded_addresses = df_excluded_addresses['Wallet Address'].str.lower().to_list()
    
#     balances_today_wo_contracts = balances_today[~balances_today['wallet_address'].isin(excluded_addresses)]
#     balances_excluded = balances_today[balances_today['wallet_address'].isin(excluded_addresses)]
#     st.write('Wallet Balances <not staking contracts>')
#     st.dataframe(balances_today_wo_contracts, width=1400, height=600)

    
   
# with tab1_col2_2:
#     excluded_address_expander = st.expander('Excluded Addresses')
#     st.write('Wallet Balances <Staking Contract, LP, etc>')
#     balances_excluded = balances_excluded.merge(df_excluded_addresses, how='left', left_on='wallet_address', right_on='Wallet Address')
#     balances_excluded = balances_excluded[['date', 'Name', 'cumsum','Wallet Address']]
#     st.dataframe(balances_excluded, width=1400, height=600)
    
# with excluded_address_expander:
#     st.write('Staking contracts, DAO Multisigs, and Markets are excluded')
#     st.dataframe(df_excluded_addresses)

# #----------------------------------------------------------------------------------------------------------------------------#
# #Add section where the user can input a specific wallet address and get stats back.
# with tab1:
#     st.header('Individual Stats')
    
#     wallet_address = st.text_input('Input wallet wallet address: ', value='0xa0a89db1c899c49f98e6326b764bafcf167fc2ce', placeholder='0xa0a89db1c899c49f98e6326b764bafcf167fc2ce')
#     col1_indiv_stats, col2_indiv_stats = st.columns((1,1))
#     specific_balances = balances[balances['wallet_address']== wallet_address.casefold()]   #[['date', 'cumsum']]
#     specific_balances = specific_balances.sort_values(by='date', ascending=False)
    
# with col1_indiv_stats:
#     st.dataframe(specific_balances[['date', 'wallet_address', 'cumsum']])
    
# with col2_indiv_stats:
#     st.write('Wallet Balance over Time')
#     wallet_bal_chart = chart = alt.Chart(specific_balances).mark_area().encode(
#         x = 'date:T',
#         y='cumsum:Q',
#         # size = 'amount:Q',
#         tooltip = ['date:T', 'cumsum:Q']
#     )
#     st.altair_chart(wallet_bal_chart, use_container_width=True)
    
# with tab2:
    
#     df_legion_holders_by_day = load_legion_nft_holders_over_time()
#     df_legion_holders_by_day_total = df_legion_holders_by_day[df_legion_holders_by_day['address']!='0x0000000000000000000000000000000000000000']
#     df_legion_holders_by_day_total = (df_legion_holders_by_day_total[['date','cumsum']]).groupby('date')['cumsum'].sum().reset_index()
    
    
    
#     # df=df_legion_holders_by_day_total.groupby(['date'])['cumsum'].sum().reset_index()
#     df_legion_holders_by_day = df_legion_holders_by_day[df_legion_holders_by_day['cumsum']>0].sort_values('date', ascending=False).drop(columns={'Unnamed: 0'})
#     df_unique_legion_holders = unique_legion_holders()
    
#     st.header('NFT Stats')   
#     st.metric('Number of Legion NFTs', df_legion_holders_by_day_total['cumsum'].iloc[-1])
#     col1_nft_stats, col2_nft_stats = st.columns((2,1))

#     st.write('Number of Unique Holders over Time')
#     unique_legion_chart = chart = alt.Chart(df_unique_legion_holders).mark_area().encode(
#         x = 'date:T',
#         y='unique_holders:Q',
#         # color='wallet_address:N',
#         # size = 'amount:Q',
#         tooltip = ['date:T', 'unique_holders:Q']
#     )
#     st.altair_chart(unique_legion_chart, use_container_width=True)
# with col1_nft_stats:
#     st.write('Number of Legion NFT over Time')
#     legion_chart = alt.Chart(df_legion_holders_by_day_total).mark_area().encode(
#     x = 'date:T',
#     y='cumsum:Q',
#     # color='wallet_address:N',
#     # size = 'amount:Q',
#     tooltip = ['date:T', 'cumsum:Q']
#     )
#     st.altair_chart(legion_chart, use_container_width=True)

# with col2_nft_stats:
#     st.dataframe(df_legion_holders_by_day, width=1400, height=600)    
    
# with tab3:
#     st.header('Trove Marketplace')
#     collections = thegraph.get_collections()
    
#     option = st.selectbox(
#      'Select Collection...',
#      collections)

#     st.write('You selected:', option)