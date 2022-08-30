import streamlit as st
import pandas as pd
import plotly.figure_factory as ff
import altair as alt
from datetime import date
import numpy as np

st.set_page_config(layout='wide')
pd.set_option('display.precision', 2)

header = st.container()
dataset = st.container()
legion_tokens = st.container()

st.sidebar.markdown("### Treasure Ecosystem Overview")
st.sidebar.markdown("This app will go over the basics of the Treasure Ecosystem.")

with header:
    st.title('Treasure Ecosystem')
    

#----------------------------------------------#
#Page Layout
#The page will be 3 columns (column 1: sidebar, column 2, column3)
col1 = st.sidebar
col2, col3 = st.columns((2,1))    

tab1, tab2, tab3 = st.tabs(['Magic Token', 'Legion', 'Other'])
# pd.options.display.float_format = "{:,.0f}".format


expander_test = st.expander
#---------------------------------------------#

@st.cache
def load_minted_over_time():
    return pd.read_csv('./MAGIC Minted over Time.csv')
def load_daily_balances_and_net_change():
    return pd.read_csv('./magic_token_daily_change_and_wallet_bal.csv')
def load_excluded_addresses():
    return pd.read_csv('./excluded_addresses.csv')
def load_balances_by_day():    
    return pd.read_csv('./balances_by_day.csv')
def load_supply_over_time():
    return pd.read_csv('./supply_over_time.csv')
def load_legion_nft_holders_over_time():
    return pd.read_csv('./legion_holders_by_day.csv')
def unique_legion_holders():
    return pd.read_csv('./unique_legion_holders.csv')
# with st.expander('About this app'):
#   st.write('This app shows the various ways on how you can layout your Streamlit app.')
# #   st.image('https://streamlit.io/images/brand/streamlit-logo-secondary-colormark-darktext.png', width=250)
# with expander_test('expander'):
    # tab1, tab2, tab3 = st.tabs(['Magic Token', 'Legion', 'Other'])


with tab1:
    st.header('$MAGIC Token')
    tab1_col1, tab1_col2, tab1_col3 = st.columns((1,1,1))
with tab1_col1:
    st.header('Magic Supply Growth')
    # minted_over_time = pd.read_csv('~/Documents/skycatcher/TreasureDAO/MAGIC Minted over Time.csv')
    # minted_over_time = load_minted_over_time()
    minted_over_time = load_supply_over_time()
    minted_over_time['amount'] = minted_over_time['amount'].apply(lambda x: -1*x)
    minted_over_time['cumsum'] = minted_over_time['cumsum'].apply(lambda x: -1 * x)
    # minted_over_time.style.format({'amount': '{:,.0f}'})
    total_magic_supply = abs(minted_over_time['cumsum'].iloc[-1])
    
    # total_magic_supply = format(total_magic_supply, '{:,.0f}')
    # total_magic_supply.style.format({"amt_minted":"{:,.0f}"})
    # st.metric('Total MAGIC Supply', "{:,.0f}".format(total_magic_supply))
    st.metric('Total MAGIC Supply', "{:,.0f}".format(total_magic_supply))
    # st.line_chart(minted_over_time, x='date', y=['cumsum', 'amount'])
    chart = alt.Chart(minted_over_time).mark_area().encode(
        x = 'date:T',
        y='cumsum:Q',
        tooltip = ['date:T', 'amount:Q', 'cumsum:Q']
    )
    st.altair_chart(chart, use_container_width=True)
    
with tab1_col2:
    st.header('Current Wallet Balances')
    # balances = pd.read_csv('/home/stubbs/Documents/skycatcher/TreasureDAO/magic_token_daily_change_and_wallet_bal.csv')
    balances = load_balances_by_day()
    balances.drop(balances.columns[0], axis=1, inplace=True)
    balances['date'] = pd.to_datetime(balances['date']).dt.date
    balances = balances.sort_values('cumsum', ascending=False)
    balances_today = balances[balances['date'] == balances['date'].max()][['date','wallet_address','cumsum']]
    # print(balances_today.head())
    # balances_today = balances_today.sort_values(by=['cumsum'], ascending=[False])#.style.format({'cumsum': '{:,.0f}'})
    # print(balances_today.head())
    
    df_excluded_addresses = load_excluded_addresses()[['Name', 'Wallet Address']]
    excluded_addresses = df_excluded_addresses['Wallet Address'].str.lower().to_list()
    
    
    # tab1_col2_c1, tab1_col2_c2 = st.columns((1,1))
    
    
    
    # balances_today.style.format({'cumsum': '{:,.0f}'})
    balances_today_wo_contracts = balances_today[~balances_today['wallet_address'].isin(excluded_addresses)]
    balances_excluded = balances_today[balances_today['wallet_address'].isin(excluded_addresses)]
    # st.dataframe(balances_today_wo_contracts, width=1400, height=600)
    # with tab1_col2_c1:
    st.write('Wallet Balances <not staking contracts>')
    # st.dataframe(balances_today_wo_contracts, width=1400, height=600)
    st.dataframe(balances_today_wo_contracts, width=1400, height=600)
# with tab1_col2_c2:

    
   
with tab1_col3:
    excluded_address_expander = st.expander('Excluded Addresses')
    st.write('Wallet Balances <Staking Contract, LP, etc>')
    balances_excluded = balances_excluded.merge(df_excluded_addresses, how='left', left_on='wallet_address', right_on='Wallet Address')
    balances_excluded = balances_excluded[['date', 'Name', 'cumsum','Wallet Address']]
    st.dataframe(balances_excluded, width=1400, height=600)
    
with excluded_address_expander:
    st.write('Staking contracts, DAO Multisigs, and Markets are excluded')
    st.dataframe(df_excluded_addresses)

    # st.dataframe(balances_excluded, width=1400, height=600)

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

    
    
    
    
    # st.write(df_legion_holders_by_day_total.head())
    # st.dataframe(df_legion_holders_by_day_total, width=1400, height=600)
    
    

    
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
    
    
    
# st.line_chart(specific_balances, x='date', y=['amount', 'cumsum'])
# with col2:
#     st.header('$MAGIC Token')
#     minted_over_time = pd.read_csv('~/Documents/skycatcher/TreasureDAO/MAGIC Minted over Time.csv')
#     st.metric('Total MAGIC Supply', minted_over_time['amt_minted'].iloc[-1])
    
    # st.line_chart(minted_over_time, x='date', y=['amt_minted', 'amount'])
    
    
    # # data = pd.read_csv('/home/stubbs/Documents/skycatcher/TreasureDAO/magic_token_daily_change_and_wallet_bal.csv')
    # data = data.sort_values(by=['date', 'cumsum'], ascending=[False, False])
    # data.drop(data.columns[0], axis=1, inplace=True)
    # data['date'] = pd.to_datetime(data['date'])
    # # data.drop(columns=[0], inplace=True).reset_index()
    # st.dataframe(data, width=1400, height=400)
    
    
    # magic_stuff = data[data['cumsum'] > 10000]
    
    # wallet_balances = alt.Chart(magic_stuff).mark_area().encode(
    # x="date:T",
    # y=alt.Y("cumsum:Q", stack="normalize"),
    # color="address:N"
    # )
    
    # st.altair_chart(wallet_balances, use_container_width=True)
    
    # #Create histogram of the data
    # hist_data = data[(data['date'] == data['date'].max()) & (data['cumsum']>10000)][['address', 'cumsum']]
    # # hist_data.hist()
    # hist_values = np.histogram(hist_data[date], 15)
    # st.bar_chart(hist_values)
    # brush = alt.selection_interval(encodings=['x'])
    # base = alt.Chart(hist_data)
    # bar = base.mark_bar().encode(
    # x=alt.X('cumsum:Q', bin=True, axis=None),
    # y='count()'
    # )
    # rule = base.mark_rule(color='red').encode(
    # x='mean(cumsum):Q',
    # size=alt.value(5)


# with col3:
#     balances = pd.read_csv('/home/stubbs/Documents/skycatcher/TreasureDAO/magic_token_daily_change_and_wallet_bal.csv')
#     balances.drop(balances.columns[0], axis=1, inplace=True)
#     balances['date'] = pd.to_datetime(balances['date'])
#     balances_today = balances[balances['date'] == balances['date'].max()][['address', 'cumsum']]
#     balances_today = balances_today.sort_values(by=['cumsum'], ascending=[True])
#     st.dataframe(balances, width=1400, height=400)



    
    
# with legion_tokens:
#     st.header('Unique NFT Holders over Time')
#     # st.write('Unique NFT Holders over Time')
#     legion_token_data = pd.read_csv('~/Documents/skycatcher/TreasureDAO/unique_legion_holders.csv')
#     legion_token_data
    
#     legion_token_data = legion_token_data.rename(columns={0:'unique_holders'})
#     st.metric('Unique Legion Holders', legion_token_data['unique_holders'].iloc[-1])
#     st.line_chart(legion_token_data, x='date', y='unique_holders')
    
#     # print(legion_token_data)
#     st.header('Legion Holders')
    
    
#     st.dataframe('')
    