import ssl
import streamlit as st
import plotly.express as px
import pandas as pd
import altair as alt
from datetime import datetime, date
import datetime as dt
import numpy as np
import os
import io
# from dotenv import load_dotenv
import boto3
import requests
import time
from datetime import timedelta
from PIL import Image


from st_aggrid import AgGrid, GridOptionsBuilder

import sys
sys.path.append('./modules/')
import nfts
import magic_token
import methods

from PIL import Image
from urllib.request import urlopen


# import thegraph
# from dotenv import load_dotenv
# load_dotenv()

#---------------------------------------------------------------------------------------------------------------------------#
#Use a try/except clause to get the environment variables for access to AWS S3 bucket whether running locally or in streamlit app
try:
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

except:
    AWS_ACCESS_KEY_ID = st.secrets['AWS_ACCESS_KEY_ID']
    AWS_SECRET_ACCESS_KEY = st.secrets['AWS_SECRET_ACCESS_KEY']

client = boto3.resource('s3', aws_access_key_id = AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
s3_bucket = "stubbs-file-storage-streamlit"
region = "us-west-1"

#Set number of seconds that data should be cached
#Initially set the time to be 24 hours
ttl_time_seconds = 60*60*24

@st.experimental_memo
def get_magic_prices():
    time.sleep(0.1)
    try:
        magic_prices = magic_token.get_magic_eth_price()
    except:
        st.write('The API failed to return values')
        magic_prices = pd.DataFrame()
    return magic_prices

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
@st.experimental_memo(ttl=ttl_time_seconds)
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
st.set_page_config(page_title='Treasure Ecosystem by Skycatcher', layout='wide')
# with open('./treasure-overview/style.css') as f:
#     st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
pd.set_option('display.precision', 2)
title_col=st.columns((2,2,6))
with title_col[0]: st.image('https://skycatcher.xyz/images/logo-white.svg')


with title_col[1]: st.image('https://treasure.lol/build/_assets/logo-H7EDAVK3.png')
with title_col[2]: 
    
    url = 'https://treasure.lol/build/_assets/hero-HQRGR2CG.png'
    img = Image.open('./modules/magic_banner1400w.png')
    cont_test = st.container()
    with cont_test:
        img.resize((round(img.size[0]*0.5), round(img.size[1]*0.5)))
        st.image(img)
        # st.image('https://treasure.lol/build/_assets/hero-HQRGR2CG.png')
header = st.container()
# dataset = st.container()
# legion_tokens = st.container()

#---------------------------------------------------------------------------------------------------------------------------#
#Create a sidebar with links to important sites
st.sidebar.markdown("### Treasure Ecosystem Overview")
st.sidebar.markdown("This app will go over the basics of the Treasure Ecosystem.")
st.sidebar.markdown("Link to BridgeWorld: [BridgeWorld](https://bridgeworld.treasure.lol/)")
st.sidebar.markdown("Link to Trove Marketplace: [Trove](https://trove.treasure.lol/)")

st.sidebar.markdown("### Harvesters: ")
st.sidebar.markdown("[docs]('https://docs.treasure.lol/cartridges/bridgeworld/harvesters')")
st.sidebar.markdown("[Harvester Leaderboard]('https://bridgeworld.treasure.lol/harvesters/leaderboard')")

#---------------------------------------------------------------------------------------------------------------------------#

with header:
    st.title('Treasure Ecosystem')
    

#----------------------------------------------#
#Page Layout
#The page will be 3 columns (column 1: sidebar, column 2, column3)
col1 = st.sidebar
col2, col3 = st.columns((2,1))    

tab1, tab_sink, tab2, tab3,  = st.tabs(['Magic Token', 'Magic Sinks', 'NFTs', 'Trove'])



# expander_test = st.expander
# #---------------------------------------------#

    


with tab1:
    
    
    st.header('$MAGIC Token')
    
    #----------------------------------------------------------------------------------
    #-----------------Get CoinGecko Market Data on $MAGIC Token------------------------
    selected_filter='usd/magic'
    magic_prices=get_magic_prices()
    print(magic_prices)
    
    @st.experimental_memo(ttl=ttl_time_seconds)
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
    magic_prices = get_magic_prices()
###-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
###-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
###                                                                     Overall Market Stats
###-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
###-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


    trading_pair_select_col, tab1_col1_cg, tab1_col2_cg, tab1_col3_cg = st.columns((1,2,2,2), gap='medium')
    with trading_pair_select_col:
        tradingpair_selection_dict = {'USD/MAGIC': 'usd/magic', 'MAGIC/ETH': 'magic/eth', 'ETH/MAGIC':'eth/magic', 'USD/ETH':'usd/weth', 'ETH/USD': 'weth/usd'}
        # magic_prices = magic_token.get_magic_eth_price()
        selectbox_magic = st.selectbox(label='Choose Trading Pair:', options=['USD/MAGIC', 'MAGIC/ETH', 'ETH/MAGIC', 'USD/ETH', 'ETH/USD'],  key='selectbox_magic')
        
    with tab1_col1_cg:
        current_price_df = cg_prices.sort_values('datetime', ascending=False)
        price_array = np.array(current_price_df['price'])
        current_price = price_array[0]
        prev_price = price_array[1]
        
        delta = 100*(current_price - prev_price)/prev_price
        st.metric('Current Magic Price', value=f'${current_price:,.3f}', delta=f'{delta:,.2f}%')
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
    
    tab1_chart_selection_col1, tab1_chart_selection_col2, tab1_chart_selection_col3 = st.columns((1,1,3)) 
        
    if selectbox_magic in tradingpair_selection_dict:
        # print(f"selectbox_magic was in the dictionary: {selectbox_magic} in {dict} : {dict[selectbox_magic]}")
        data_type_selection_mapped=tradingpair_selection_dict[selectbox_magic]
        # print(f'returning data_type_selection_mapped: {data_type_selection_mapped}, type: {type(data_type_selection_mapped)}')
    else:
        print(f"the bugger wasn't in the tradingpair_selection_dict\nselectbox_magic: {selectbox_magic} type: {type(selectbox_magic)}")
        data_type_selection_mapped = selectbox_magic
    
    
    magic_prices_filtered = magic_prices[['datetime', data_type_selection_mapped]]

    df = magic_prices_filtered.copy()    
    fig = px.line(df, 
                  x="datetime", 
                  y=data_type_selection_mapped)
    # Add range slider
    fig.update_layout(
        hovermode="x unified", 
        height=600,
        title={
            'text': '<b>Historical Price Plot<b>',
            'xanchor': 'left',
            'y':0.95,
            'yanchor':'top'
        },
        title_pad=dict(
            b=20
            ),
        title_font=dict(
            size = 30,
        ),
        # template="plotly_white",
        hoverdistance=-1,
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    
                    dict(count=7,
                        label="1w",
                        step="day",
                        stepmode="backward"),
                    dict(count=1,
                        label="1m",
                        step="month",
                        stepmode="backward"),
                    dict(count=3,
                        label="3m",
                        step="month",
                        stepmode="backward"),
                    dict(count=1,
                        label="YTD",
                        step="year",
                        stepmode="todate"),
                    dict(count=1,
                        label="1y",
                        step="year",
                        stepmode="backward"),
                    dict(step="all")
                ]), 
                font_color='black'
            ),
            rangeslider=dict(
                visible=True
            ),
            type="date"
        )
    )
    fig.update_layout(
        xaxis_domain=[0.05, 1.0],
        yaxis_domain=[0, 0.9]
    )
    fig.update_layout(
        hoverlabel=dict(
            font_size=20,
        )
    )
    fig.update_traces(
        hovertemplate=
        "MAGIC Price (USD): $%{y:.2f}"
    )
    fig.update_layout(
        margin=dict(
            l=0,
            r=20,
            t=45,
            b=35
        ),
        # paper_bgcolor='#333335'
    )
    fig.add_annotation(
        dict(
            font=dict(
                color='white',
                size=15
            ),
            x=0,
            y=-0.35,
            showarrow=False,
            text= "Market Information: CoinGecko API",
            textangle=0,
            xanchor='left',
            xref="paper",
            yref='paper'
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    st.write('Market Information: CoinGecko API')
# fig.show()
#---------------------------------------------------------------------------------------------------------------------------------------------------#
#                                                                                                                                                   #
#                                              Token Distribution Section                                                                           #
#                                                                                                                                                   #
#---------------------------------------------------------------------------------------------------------------------------------------------------#
    
    df_wallet_balances = load_balances_by_day_parquet()
    daily_total_per_wallet = df_wallet_balances.groupby(['date', 'address'])['cumsum'].sum().reset_index()
    total_supply_historical = df_wallet_balances.groupby('date')['cumsum'].sum().reset_index()
    
    mask = daily_total_per_wallet['date']>'2022-09-01'
    daily_total_per_wallet[mask]
    
    current_date = daily_total_per_wallet['date'].values.max()
    earliest_date = daily_total_per_wallet['date'].values.min()
    total_mask = (daily_total_per_wallet['date']==daily_total_per_wallet['date'].values.max()) & (daily_total_per_wallet['cumsum'] == daily_total_per_wallet['cumsum'].values.max())
    total_mask_alltime = (daily_total_per_wallet['cumsum'] == daily_total_per_wallet['cumsum'].values.max())
    
    
    
    # current_largest_wallet = daily_total[wallet_mask]
    overall_largest_balance = daily_total_per_wallet[total_mask_alltime]
    max_wallet_size=overall_largest_balance['cumsum'].values.max()
    
    current_date_max_mask = (daily_total_per_wallet['date']==current_date) ###& (daily_total['cumsum']==daily_total['cumsum'].values.max())
     
    max_wallet_size = daily_total_per_wallet[current_date_max_mask]['cumsum'].values.max()
    
    print("\n\n\n\n#---------------------------------------------------------------#")
    print(overall_largest_balance)
    print("#---------------------------------------------------------------#\n\n\n\n")
    total_array = np.array(daily_total_per_wallet['cumsum'])
    total_array_lag=np.concatenate(([0], total_array[:-1]))
    daily_change = total_array-total_array_lag
    daily_total_per_wallet['change'] = daily_change
    
    tab1_col1, tab1_col2 = st.columns((1,2))
    st.header('Current Wallet Balances')
    
    tab1_col1_2, tab1_col2_2, tab1_col2_3 = st.columns((1,1,4))
    
    with tab1_col1_2:
        historical_total_supply_array = np.array(total_supply_historical['cumsum'])
        current_supply = historical_total_supply_array[-1]
        previous_supply = historical_total_supply_array[-31]
        
        change_perc = (current_supply - previous_supply)/previous_supply
        change_abs = (current_supply - previous_supply)
        # change = 100*(np.array(total_supply_historical['change'])[-1]/np.array(daily_total_per_wallet['cumsum'])[-2])
        st.metric(label="Current MAGIC Supply", value = f'{current_supply:,.0f}', delta=f'{change_abs:,.0f} MAGIC over 30 days')
    with tab1_col2_2:
        change_last_14_days_array=np.array(daily_total_per_wallet['change'])[-1]
        average_daily_change = np.sum(change_last_14_days_array)
        
        #Get yearly inflation based on 14 day average
        # (365*average_daily_change)
        
        change = np.array(daily_total_per_wallet['change'])[-1]/np.array(daily_total_per_wallet['cumsum'])[-2]
        st.metric(label="Increase (Decrease) of Total Supply", value = f'{change:,.0f}')
        
    if 'max_wallet_size_set' not in st.session_state:
        st.session_state.max_wallet_size = max_wallet_size
    if 'min_wallet_size_set' not in st.session_state:
        st.session_state.max_wallet_size = 0
    if 'max_wallet_size_set' not in st.session_state:
        st.session_state.max_wallet_size_set = max_wallet_size
    if 'min_wallet_size_set' not in st.session_state:
        st.session_state.min_wallet_size_set = 0
    
    wallet_filter_col = st.columns((1,1,1, 3))    
    ###-------------------------------------------------------------------------------
    ###    Column 1
    ###-------------------------------------------------------------------------------
    with wallet_filter_col[0]:
        min_wallet_user_input = st.number_input(label ="Do you want to filter by a minimum wallet balance?", min_value =0.0, max_value = st.session_state.max_wallet_size_set, value=100.0, step=100.0, help='(Optional) Set a minimum wallet balance. The default is 100.')
        st.session_state.min_wallet_size_set = min_wallet_user_input
    
    ###-------------------------------------------------------------------------------
    ###     Column 2
    ###-------------------------------------------------------------------------------
    with wallet_filter_col[1]:
        max_wallet_user_input = st.number_input(label ="Do you want to filter by a maximum wallet balance?",min_value=100.0, max_value=float(overall_largest_balance.iloc[0]['cumsum']), value = float(max_wallet_size), step=100.0, help='(Optional) Set a maximum wallet balance. The default is the current largest wallet.')
        if (max_wallet_user_input is None) | (max_wallet_user_input == 0):
            st.session_state.max_wallet_size_set = overall_largest_balance
            st.session_state.max_wallet_size_entered = False
        else:
            st.session_state.max_wallet_size_entered = True
        st.session_state.max_wallet_size_set = max_wallet_user_input
        
    ###------------------------------------------------------------------------------
    ###      Column 3
    ###-----------------------------------------------------------------------------
    with wallet_filter_col[2]:
        st.metric("Largest Wallet", value = f"{max_wallet_size:,.0f}")
        
    # with wallet_filter_col[3]:
        # image = "https://app.rlm.land/_next/image?url=%2Fassets%2Fadventurers%2F8.jpeg&w=1920&q=75"
        
        # st.image(image, caption='This is my AoV', width=None, use_column_width='auto', clamp=False, channels="RGB", output_format="auto")
    
    if st.session_state.max_wallet_size_entered:
        mask = (df_wallet_balances.index >= "2022-01-01") & (df_wallet_balances['cumsum']>=st.session_state.min_wallet_size_set) & (df_wallet_balances['cumsum']<st.session_state.max_wallet_size_set)
    else: 
        mask = (df_wallet_balances.index >= "2022-01-01") & (df_wallet_balances['cumsum']>=st.session_state.min_wallet_size_set)
    filtered_time = df_wallet_balances[mask]
    daily_address_with_wallet_size = filtered_time.groupby('date')['address'].count().reset_index().sort_values('date', ascending=True)
    
    # filtered_time    
    
    # fig = px.area(daily_total, x="date", y='cumsum', title='MAGIC Supply')
    # fig.update_layout(hovermode="x unified")
    # st.plotly_chart(fig, use_container_width=True)
    
    
    st.subheader("MAGIC Holder Activity Levels")
    cd=np.datetime64(current_date, 'ms').astype(dt.date)
    st.subheader(f"As of {cd.strftime('%Y-%m-%d')}")
    
    daily_number_of_holders = daily_address_with_wallet_size
    num_holders = np.array(daily_address_with_wallet_size['address'].values)
    st.write(f"{num_holders[-1]:,.0f} wallets hold {st.session_state.min_wallet_size_set} or more MAGIC")
    
    ###---------------------------------------------------------------------------------------------------------------------------------
    ###---------------------------------------------------------------------------------------------------------------------------------
    ###       Get Wallet Size for Different Groups
    ###---------------------------------------------------------------------------------------------------------------------------------
    def write_boolean_mask(min_mask_value, max_mask_value):
        date_mask = df_wallet_balances.index==current_date
        balance_mask = (df_wallet_balances['cumsum'] > min_mask_value) & (df_wallet_balances['cumsum'] <= max_mask_value)
        total_mask = date_mask & balance_mask

        return total_mask
    
    def write_boolean_mask_historical(min_mask_value, max_mask_value, _date):
        date_mask = df_wallet_balances.index==_date
        balance_mask = (df_wallet_balances['cumsum'] > min_mask_value) & (df_wallet_balances['cumsum'] <= max_mask_value)
        total_mask = date_mask & balance_mask

        return total_mask
    
    def get_count_addresses(masked_df_list):
        len(set(masked_df_list['address'].values))
    
    user_selected_date = st.date_input(label='Select a date for comparison.', value = pd.to_datetime(current_date) - pd.Timedelta(days=30), min_value = pd.to_datetime(earliest_date), help='The defaul value is for 30 days ago')
    user_selected_date = user_selected_date.strftime('%Y-%m-%d')
    
    groups = [(0, 0.5),(0.5,1), (1, 10), (10,100), (100, 1000), (1000,10000), (10000, 100000), (100000, max_wallet_size)]
    masked_groups = []
    num_addresses = []
    i=0
    bigOne = st.columns(len(groups))
    
    
    # user_selected_date = st.date_input(label='Select a date for comparison.', value = pd.to_datetime(current_date) - pd.Timedelta(days=30), min_value = pd.to_datetime(earliest_date), help='The defaul value is for 30 days ago')
    st.subheader("Distribution of MAGIC Token:")
    for group in groups:
        name = f"group_{i}"
        min_value = group[0]
        max_value = group[1]
        
        curr_boolean_mask = write_boolean_mask(min_value, max_value)
        historical_boolean_mask = write_boolean_mask_historical(min_value, max_value, user_selected_date)
        
        curr_filtered_df = df_wallet_balances[curr_boolean_mask]
        historical_filtered_df = df_wallet_balances[historical_boolean_mask]
        
        curr_num_addresses = len(set(curr_filtered_df['address'].values))
        historical_num_addresses = len(set(historical_filtered_df['address'].values))
        
        change_perc = 100*(curr_num_addresses-historical_num_addresses)/historical_num_addresses
        
        print(f"*-------------------------*\nMin Value: {min_value}\nMax Value:{max_value}\nNumber of Wallets: {curr_num_addresses}\n*-------------------------*\n")
        
        group_dict = {i: {'name':name, 'min_value': min_value, 'max_value' : max_value, 'num_addresses':curr_num_addresses}}
        masked_groups.append(curr_filtered_df)
        num_addresses.append(curr_num_addresses)
        
        
        
        
        if min_value < 1:
            html_str = f"""
                <p style="text-align:center, font-size: larger">
                <b>{min_value:,.2f} MAGIC</b> to <b>{max_value:,.2f} MAGIC</b></p><br>
                <p style="text-align:center">{curr_num_addresses:,.0f}    ||    {historical_num_addresses:,.0f}<br>
                {change_perc:,.1f}%
                </p>"""
            bigOne[i].markdown(html_str, unsafe_allow_html=True)
            # bigOne[i].metric(f'{min_value:,.2f} MAGIC to {max_value:,.0f} MAGIC', value=f'{new_num_addresses:,.0f}')
        else:
            html_str = f"""
                <p style="text-align:center, font-size: larger">
                <b>{min_value:,.0f} MAGIC</b> to <b>{max_value:,.0f} MAGIC</b></p><br>
                <p style="text-align:center">{curr_num_addresses:,.0f}    ||    {historical_num_addresses:,.0f}<br>
                {change_perc:,.1f}%
                </p>"""
            bigOne[i].markdown(html_str, unsafe_allow_html=True)
            
            # bigOne[i].metric(f'{min_value:,.0f} MAGIC to {max_value:,.0f} MAGIC', value=f'{new_num_addresses:,.0f}')
        i = i + 1
        
        
        
    # column_container = st.container()    
    # holders_columns = st.columns(len(group_dict))
    # print(holders_columns)
    # for i in range(len(holders_columns)):
    #     with column_container:

    #         name = group_dict[i]['name']
    #         min_value = group_dict[i]['min_value']
    #         max_value = group_dict[i]['max_value']
            
    #         label_text = f"#Holders:\n {min_value} < Wallet Balance <= {max_value} MAGIC"
    #         with holders_columns[i]:
    #             # st.metric(label=label_text, value=group_dict[i]['num_addresses'] )
    #             print(label_text)
    #             st.write(label_text)
            
        
    # st.write(label_text)    
        
    # for holder_column in holders_columns:

    # for i in range(len(group_dict)):
    # # for k in group_dict:
    #     # group_dict[k]
    #     # for i in range(0, len(num_addresses)):
    #     with holders_columns[i]:
    #         name = group_dict[i]['name']
    #         min_value = group_dict[i]['min_value']
    #         max_value = group_dict[i]['max_value']
            
    #         label_text = f"# Holders:\n {min_value} < Wallet Balance <= {max_value} MAGIC"
    #         st.metric(label=label_text, value=group_dict[i]['num_addresses'] )
        
    #         st.write(label_text)
    # masked_groups[0]
        
    group0 = write_boolean_mask(0,10000)
    group1=write_boolean_mask(10000,1000000)
    group2=write_boolean_mask(1000000,10000000)
    group3=write_boolean_mask(1000000, max_wallet_size) 
    
    groups = [group0, group1, group2, group3]   
    # date_mask = df_wallet_balances.index==current_date
    
    # group_mask = date_mask & (df_wallet_balances['cumsum'] < 1000)
    
    # df_wallet_balances[group_mask]
    
    # groups=['<10,000 MAGIC', '10,000 - 100,000 MAGIC', '100,000 - 1M MAGIC', 'More than 1M MAGIC']
    
    
    # def get_mask(df):
    #     mask = df['']
    # group_def_masks = {'<10,000 MAGIC': {'min_value': 0, 'max_value': 10000},
    #                    '10,000 - 100,000 MAGIC': {'min_value':10000, 'max_value':100000}}
    
    
    # df_balances_group=df_wallet_balances
    
    # for mask in mask_list:
    #     df_balances_group[mask]['addres']
    #     len()
    
    
    # with num_visualization1[0]:
    #     mask = df_balances_group['cumsum'] < 10000
        
        
    #     st.metric("<10,000 MAGIC", value=df_balances_group[mask], delta="50")
            
    # with num_visualization1[1]:
    #     st.metric("10,000 - 100,000 MAGIC", value=200, delta="50")
    # with num_visualization1[2]:
    #     st.metric("100,000 - 1,000,000 MAGIC", value=200, delta="50")
    # with num_visualization1[3]:
    #     st.metric(label="More than 1M MAGIC", value=f"{num_holders[-1]:,.0f}")
    #     st.write(f"Number of Wallets with {st.session_state.min_wallet_size_set} or more MAGIC")
    #     # st.write(f"Currently there are {num_holders[-1]:,.0f} wallets that hold {st.session_state.min_wallet_size_set} or more MAGIC")
        
        
    # st.write(label=" d ")
    # image = "https://app.rlm.land/_next/image?url=%2Fassets%2Fadventurers%2F17.jpeg&w=1920&q=75"
    # st.image(image, caption='This is my AoV', width=None, use_column_width='auto', clamp=False, channels="RGB", output_format="auto")   
    
        
    # with num_visualization1[1]:
    #     image = "https://app.rlm.land/_next/image?url=%2Fassets%2Fadventurers%2F20.jpeg&w=1920&q=75"
    #     st.image(image, caption='This is my AoV', width=None, use_column_width='auto', clamp=False, channels="RGB", output_format="auto")    
    num_visualization1 = st.columns((1,6))                    
    with num_visualization1[0]:
        num_today = num_holders[-1]
        interval_30days = num_holders[-31]
        
        change = 100*(num_today - interval_30days)/interval_30days
        
        st.metric('Current # Wallets', value = f"{num_today:,.0f}", delta=f"{change:,.2f}% (30 days)")
    with num_visualization1[1]:    
        x_array = np.array(daily_address_with_wallet_size.index)
        y_array = daily_address_with_wallet_size.loc[:]
        
        fig2 = px.line(daily_address_with_wallet_size, 
                    x='date', y='address', 
                    title=f'Daily Number of Wallet with More than {st.session_state.min_wallet_size_set} MAGIC'
                        )
        fig2.update_layout(
            hovermode="x unified",
            hoverlabel=dict(
                font_size=20
            ))
        fig2.update_traces(
            hovertemplate=
            "Date: %{x}<br>" +
            "# of Wallets: %{y:,.0f}",
            showlegend=False
        )
        
        st.plotly_chart(fig2, use_container_width=True)
        
    
        
        
        

    # image = "https://app.rlm.land/_next/image?url=%2Fassets%2Fadventurers%2F10.jpeg&w=1920&q=75"
    # st.image(image, caption='This is my AoV', width=None, use_column_width='auto', clamp=False, channels="RGB", output_format="auto")    
    
    
    ###---------------------------------------------------------------------------------------------------------------------------------
    ###---------------------------------------------------------------------------------------------------------------------------------
    ###       Get Wallet Size for Different Groups
    ###---------------------------------------------------------------------------------------------------------------------------------
    @st.cache
    def get_magicTransfers():
        return methods.get_magicTransfers()
    
    
    st.markdown("""
               # Magic Activity ###
               ---
               ### Let's look at how many wallets have had interactions with the MAGIC token recently. 
                """)

    
    df_magic_interactions = get_magicTransfers()
    df_inter = df_magic_interactions.copy()
    interaction_limit_min = [1, 5, 10, 20, 50, 100, 1000]

    
    interactions = df_magic_interactions.groupby('origin_from_address')['tx_hash'].count().reset_index().sort_values('tx_hash', ascending=False)
    
    first_transfer_date = df_magic_interactions['block_timestamp'].values.min()
    last_transaction_date = df_magic_interactions['block_timestamp'].values.max()
    max_interval = pd.to_datetime(last_transaction_date) - pd.to_datetime(first_transfer_date)
    st.write(first_transfer_date, last_transaction_date)
    
    interactions_per_wallet_unfiltered = interactions
    num_wallets_interactions_per_wallet_unfiltered = len(set(interactions['origin_from_address'].values))
    
    interaction_dict = [{'num_wallets': num_wallets_interactions_per_wallet_unfiltered, 'min_txns': 0, 'name': f'No Minimum # of Txns'}]
    # {num_interactions: {'name': f'# Interactions > {num_interactions}', 'min_txns': num_interactions, 'num_wallets':interactions_filtered}}

    # interactions_dict = {0 :{'label': 'None', 'num_wallets':interaction_list[0]}}
    # print(len(interactions['origin_from_address'].values), len(interactions_filtered['origin_from_address'].values))
    for num_interactions in interaction_limit_min:
        interaction_min_mask = interactions_per_wallet_unfiltered['tx_hash'] > num_interactions
        interactions_filtered=interactions_per_wallet_unfiltered[interaction_min_mask]
        
        num_wallets=len(set(interactions_filtered['origin_from_address'].values))
        
        # interaction_list.append(interactions_filtered)
        interaction_dict.append({'name': f'# Interactions > {num_interactions}', 'min_txns': num_interactions, 'num_wallets':num_wallets})

        # interaction_dict.update({f'# Interactions > {num_interactions}': {'min_txns': num_interactions, 'num_wallets':interactions_filtered}})
        
    # st.write(interaction_list)
    
    # fig_interactions = px.line(interaction_list[0], 
    #             x='date', y='address', 
    #             title=f'Daily Number of Wallet with More than {st.session_state.min_wallet_size_set} MAGIC'
    #                 )
    # fig2.update_layout(
    #     hovermode="x unified",
    #     hoverlabel=dict(
    #         font_size=20
    #     ))
    # fig2.update_traces(
    #     hovertemplate=
    #     "Date: %{x}<br>" +
    #     "# of Wallets: %{y:,.0f}",
    #     showlegend=False
    # )
    
    # st.plotly_chart(fig2, use_container_width=True)
    activity_columns = st.columns((1,1,1))
    df_interactions = pd.json_normalize(interaction_dict)
    
    df_interactions['perc']= 100*(df_interactions.loc[:,'num_wallets']/df_interactions.loc[0,'num_wallets'])
    
    
    # st.dataframe(df_interactions)
    print(df_magic_interactions.columns)
    
    date_mask = pd.to_datetime(df_magic_interactions['block_timestamp']).dt.date > date.today() - timedelta(days=30)
    prev_30_df_magic_interactions = df_magic_interactions[date_mask]
    
    day_filter_list = [1, 3, 7, 14, 21, 30, 60, 90]
    num_wallets_prev_days_list = []
    num_wallet_dict = {}

    for day in day_filter_list:
        date_mask = pd.to_datetime(df_magic_interactions['block_timestamp']).dt.date > date.today() - timedelta(days=day)
        prev_days_df_magic_interactions = df_magic_interactions[date_mask]
        num_wallets_prev_days_list.append({'date_interval': day, 'num_wallets':len(set(prev_days_df_magic_interactions['origin_from_address'].values))})
    df_recent = pd.json_normalize(num_wallets_prev_days_list)
        
    # pie_fig = px.pie(df_interactions,
    #                  x=df_interactions['label'],
    #                  y=df_interactions['num_wallets']
    # )
    
    
    df_interaction_recency = methods.activity_filteredByDateAndTxns('Get New', day_filter_list, interaction_limit_min)
    
    df_ir = df_interaction_recency.reset_index()
    df_ir.columns =['min_txns', 'timedelta', 'num_active', 'addresses']

    with activity_columns[0]:
        st.markdown('### Filter Wallets by Txns')
        st.markdown('This table filters the wallets by a minimum # of transactions.')
        st.dataframe(df_interactions[['name', 'min_txns', 'num_wallets', 'perc']], width=1000)
        
    with activity_columns[1]:
        df_recent['perc']=100*(df_recent.loc[:, 'num_wallets']/df_interactions.loc[0, 'num_wallets'])
        df_recent.columns = ['Date Interval', '# Wallets Included', '% of Total']
        
        st.markdown('### Filter by Elapsed Time Since Interaction')
        st.markdown('This table filters based on the time since interacting with MAGIC tokens.')
        st.dataframe(df_recent.sort_values('Date Interval', ascending=False), width = 500)
        
        
    with activity_columns[2]:
        
        
        st.markdown("### Now let's filter by both # of Txns and Timeframe!")
        st.markdown("More importantly - How many wallets are are recent & active?")
        st.dataframe(df_ir[['min_txns', 'timedelta', 'num_active']])
        
        
    
    date_mask_combo= [(21, 50)]
    
    
    # combo_mask = (df_magic_interactions['block_timestamp'].dt.date > date.today() - timedelta(days=date_mask_combo[0][0])) & df_magic_interactions['']
    
    
    
#---------------------------------------------------------------------------------------------------------------------------------------------------#   
#---------------------------------------------------------------------------------------------------------------------------------------------------#   
##-----------------------------------Make a Funnel Chart to See how much people are filtered out-----------------------------------------------------   


###First filter by Minimum # Txns
###------------------------------
stages = dict(
    
)


    
    
    
###
#---------------------------------------------------------------------------------------------------------------------------------------------------#   
#---------------------------------------------------------------------------------------------------------------------------------------------------#   
  
#---------------------------------------------------------------------------------------------------------------------------------------------------#   
#---------------------------------------------------------------------------------------------------------------------------------------------------#    
#---------------------------------------------------------------------------------------------------------------------------------------------------#
#                                                                                                                                                   #
#                                                             NFTs                                                                                  #
#                                                                                                                                                   #
#---------------------------------------------------------------------------------------------------------------------------------------------------#
#---------------------------------------------------------------------------------------------------------------------------------------------------#
#---------------------------------------------------------------------------------------------------------------------------------------------------#
@st.experimental_memo(ttl=ttl_time_seconds)
def get_collection_info():
    url = "https://api.thegraph.com/subgraphs/name/treasureproject/marketplace"
    query = """
            {
    collections{
        name
        id
        contract
        }
        }
    """
    response = requests.post(url, json={'query':query}).json()['data']['collections']
    collections = pd.json_normalize(response)
    return collections
# def get_collection_data():
@st.experimental_memo(ttl=ttl_time_seconds)
def get_collection_stats():
    url = "https://api.thegraph.com/subgraphs/name/treasureproject/marketplace"
    query="""
    {
    collections(where: {
        id_in:
        [
          "0xfe8c1ac365ba6780aec5a985d989b327c27670a1-0"
        , "0xfe8c1ac365ba6780aec5a985d989b327c27670a1-1"
        , "0xfe8c1ac365ba6780aec5a985d989b327c27670a1-2"
        , "0xebba467ecb6b21239178033189ceae27ca12eadf"
        , "0xf3d00a2559d84de7ac093443bcaada5f4ee4165c"
        , "0xbfeba04384cecfaf0240b49163ed418f82e43d3a"
        , "0xe83c0200e93cb1496054e387bddae590c07f0194"
        , "0xf0a35ba261ece4fc12870e5b7b9e7790202ef9b5"
        , "0x21e1969884d477afd2afd4ad668864a0eebd644c"

        , "0x6325439389e0797ab35752b4f43a14c004f22a9c"
        , "0x17dacad7975960833f374622fad08b90ed67d1b5"
        , "0xf6cc57c45ce730496b4d3df36b9a4e4c3a1b9754"
        , "0xae0d0c4cc3335fd49402781e406adf3f02d41bca"
        , "0xb16966dad2b5a5282b99846b23dcdf8c47b6132c"
        , "0xdf32aed1eb841a174cb637eaa1707026319fb563"
        , "0xd666d1cc3102cd03e07794a61e5f4333b4239f53"
        , "0xc5295c6a183f29b7c962df076819d44e0076860e"
        
        , "0xdc758b92c7311280aeeb48096a3bf4d1c1f936d4"
        , "0x3956c81a51feaed98d7a678d53f44b9166c8ed66"
        , "0xcf51e9622471fb2bf2d66226a878280eabd71778"

        , "0x0af85a5624d24e2c6e7af3c0a0b102a28e36cea3"
        , "0xc43104775bd9f6076808b5f8df6cbdbeac96d7de-1"
        , "0xc43104775bd9f6076808b5f8df6cbdbeac96d7de-2"

        , "0x4de95c1e202102e22e801590c51d7b979f167fbb"
        , "0x8762DbD391Fd90b29eccBB628CD54bD92F5Fc1f3"
        , "0x20251F0ee19917bDe625Ba9eBf79aD3b7769f673"
        , "0x8ec68F970e1c61b44B6d81c3b78Ca931C6FFc92d"
        , "0xCE3051ff2ED963406b55ef505751eF88B8f0D791"
        , "0x747910B74D2651A06563C3182838EAE4120F4277"
        , "0x09cae384c6626102abe47ff50588a1dbe8432174"
        , "0x5e0ba87362f239bDBF40E621Fa11DBD50d190389"
        , "0x00000000016c35e3613ad3ed484aa48f161b67fd"
        , "0x32A322C7C77840c383961B8aB503c9f45440c81f"
        , "0xf7fbe8eec9063aa518d11639565b018468bb4abb"
        , "0x6f2aa70c70625e45424652aed968e3971020f205"
        , "0x9f0cc315cae0826005b94462b5400849b3d39d91"
        , "0x37865fe8a9c839f330f35104eed08d4e8136c339"
        , "0x7480224ec2b98f28cee3740c80940a2f489bf352"
        , "0x381227255ef6c5d85966b78d13e4b4a4c8719b5e"
        , "0x89A8Fe072c1193A1C4cfBe4f3787f5681BaBf9ae"
        , "0x71bd1562f7e0f182f8be472151befdfb824e26be"
        , "0x5e01c1889085b528eeff5e1bee64bfe94f454703" 
        ]
    }){
    id
    name
    stats{
        floorPrice
        burned
        items
        listings
        sales
        volume
    }
    }
    }
    """
    response = requests.post(url, json={'query':query}).json()['data']['collections']
    collections = pd.json_normalize(response)
    
    collections['stats.floorPrice'] = collections['stats.floorPrice'].astype('float64')
    collections['stats.volume'] = collections['stats.volume'].astype('float64')
    
    collections['stats.floorPrice']=collections.loc[:,'stats.floorPrice']/pow(10,18)
    collections['stats.volume']=collections.loc[:, 'stats.volume']/pow(10,18)
    return collections    


with tab_sink:
    st.header("Harvesters")
    
    # @st.experimental_memo(ttl=ttl_time_seconds)
    magic_sinks=magic_token.get_magic_sinks()
    
    group_magic_sinks = magic_sinks.groupby(['sink.name','token.name'])[['token.quantity']].sum().sort_index()
    
    sink_names = np.array(magic_sinks['sink.name'].drop_duplicates())
    with st.container():
        st.subheader('Asiterra')
        
        asiterra_items = group_magic_sinks.loc['Asiterra', :].sort_values('token.quantity', ascending=False).reset_index()
        num_items = asiterra_items['token.quantity'].sum()
        st.metric(label='Tokens Staked', value = num_items)
        st.dataframe(asiterra_items, width = 700, height=700)
        
        # builder = GridOptionsBuilder.from_dataframe(asiterra_items)
        # builder.configure_column("token.quantity", header_name="Quantity")
        # AgGrid(asiterra_items, height=400, pag)
        # asiterra_stats=group_magic_sinks['Asiterra', :]
        # st.dataframe(magic_sink)
        asiterra_col, shinoba_col, kameji_col = st.columns((1,1,1))
        with asiterra_col:
            st.header('Asiterra')
            
        with shinoba_col:
            st.header('Shinoba')
            
        with kameji_col:
            st.header('Kameji')
    harvesters = ['Asiterra', 'Shinoba', 'Kameji']
["0x2ef99434b0be1511ed2a1589dc987e48298e059e",
       "0x3e455c3321ef4861dd8492d7fc099190a846458a",
       "0x737eaf14061fe68f04ff4ca8205acf538555fcc8",
       "0x85f1bfd98e190b482d5348fd6c987ae3da7a4df6",
       "0xa0515709fa0f520241659a91d868151e1ad263d8",
       "0xa0a89db1c899c49f98e6326b764bafcf167fc2ce",
       "0xb9c9ed651eb173ca7fbc3a094da9ce33ec145a29",
       "0xf6d2c864ce0bbbe3824c72995d99fab0f3a0f260",
       "0xf9e197aa9fa7c3b27a1a1313cad5851b55f2fd71"]

["Ancient Relic", "Bag of Rare Mushrooms", "Bait for Monsters",
       "Beetle Wings", "Blue Rupee", "Bottomless Elixir",
       "Cap of Invisibility", "Carriage", "Castle", "Common Bead",
       "Common Feather", "Common Relic", "Cow", "Diamond",
       "Divine Hourglass", "Divine Mask", "Donkey", "Dragon Tail",
       "Emerald", "Favor from the Gods", "Framed Butterfly", "Grain",
       "Green Rupee", "Grin", "Half-Penny", "Honeycomb",
       "Immovable Stone", "Ivory Breastpin", "Jar of Fairies", "Lumber",
       "Military Stipend", "Mollusk Shell", "Ox", "Pearl", "Pot of Gold",
       "Quarter-Penny", "Red Feather", "Red Rupee", "Score of Ivory",
       "Silver Coin", "Small Bird", "Snow White Feather",
       "Thread of Divine Silk", "Unbreakable Pocketwatch",
       "Witches Broom", "Gold Coin"]

with tab2:
    st.header('NFT Data')
    
    cartridges = ['Bridgeworld', 'Smolverse', 'Realm', 'Battlefly', 'Toadstoolz', 
                  'Tales of Elleria', 'The Lost Donkeys', 'LifeDAO', 'Knights of the Ether', 
                  'Lost SamuRise', 'Peek-A-Boo!', 'SmithyDAO']
    collection_info = get_collection_info()
    collection_stats = get_collection_stats()
    
    collection_names = np.array(collection_info['name'])
    selection_col1, selection_col2, selection_col3 = st.columns((1,1,2))
    
    with selection_col1:
        selection_radio = st.radio(label="Select Cartridge or Collection...", options=['Cartridge', 'Collection'])
        selected_cartridge = st.selectbox(label='Select Cartridge...', options=cartridges)
    with selection_col2:
        if selection_radio == 'Cartridge':
            selectbox_label = 'Select Cartridge...'
            options = cartridges
        elif selection_radio == 'Collection':
            selectbox_label = 'Select Collection...'
            options = collection_names
        # if selected_cartridge
        # selection_selectbox = st.selectbox(label=selectbox_label, options=options)
    
    nft_stats_container = st.container()
    with nft_stats_container:
        nft_stats_col1, nft_stats_col2 = st.columns((3,2))   
        
        # with nft_stats_col2:
            # if selection_selectbox in nfts.cartridge_images:
            #     st.image(nfts.cartridge_images[selection_selectbox])
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