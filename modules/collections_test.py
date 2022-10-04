# This is a test
import collections
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
import nft_streamlit_page
import magic_token
import methods
import trove_data
import contracts

from PIL import Image
from urllib.request import urlopen

try:
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

except:
    AWS_ACCESS_KEY_ID = st.secrets['AWS_ACCESS_KEY_ID']
    AWS_SECRET_ACCESS_KEY = st.secrets['AWS_SECRET_ACCESS_KEY']

client = boto3.resource('s3', aws_access_key_id = AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
s3_bucket = "stubbs-file-storage-streamlit"
region = "us-west-1"

st.set_page_config(page_title='Treasure Ecosystem by Skycatcher', layout='wide')
pd.set_option('display.precision', 2)
title_col=st.columns((2,2,6))
with title_col[0]: st.image('https://skycatcher.xyz/images/logo-white.svg')


with title_col[1]: st.image('https://treasure.lol/build/_assets/logo-H7EDAVK3.png')
with title_col[2]: 
    
    url = 'https://treasure.lol/build/_assets/hero-HQRGR2CG.png'
    img = Image.open('./magic_banner1400w.png')
    cont_test = st.container()
    with cont_test:
        img.resize((round(img.size[0]*0.5), round(img.size[1]*0.5)))
        st.image(img)
header = st.container()       
with header:
    st.title('Treasure Ecosystem')
    

#----------------------------------------------#
#Page Layout
#The page will be 3 columns (column 1: sidebar, column 2, column3)
col1 = st.sidebar
col2, col3 = st.columns((2,1))    

tab1, tab_sink, tab_cartridge, tab_trove,  = st.tabs(['Magic Token', 'Magic Sinks', 'Cartridges', 'Trove'])

###**********************************************************************************************************###
###
###             This is where code starts - Above is just defailt from the real page
###
###
###**********************************************************************************************************###


with tab_cartridge:
    
    st.experimental_memo
    def get_collections():
        df_collections_raw=trove_data.get_collections().copy()
        
        cartridge_dict = contracts.contract_to_cartridge
        collection_dict = contracts.contract_to_name
        
        df_collections=df_collections_raw
        df_collections['cartridge'] = df_collections_raw.loc[:, 'collection_id'].map(cartridge_dict)
        df_collections['collection'] = df_collections_raw.loc[:, 'collection_id'].map(collection_dict)
        
        df_collections.dropna(subset=['collection', 'cartridge'], inplace=True)
        df_collections.sort_values(['cartridge', 'collection'], ascending=[True, True], inplace=True)
        
        return df_collections
    def get_collection_info():
        return trove_data.get_collection_info()
    
    def filter_collection_list(list_of_filters):
        mask = df_collections['cartridge'].isin(list_of_filters)
        df_collections_filter = df_collections[mask]
        collections_list = np.array(df_collections_filter['collection'].values)
        
        st.session_state.df_collections_list = collections_list
        return collections_list
    
    df_collections = get_collections()
    
    cartridge_list = np.unique(df_collections['cartridge'].sort_values(ascending=True).values)
    collection_list = np.array(df_collections['collection'].values)
    default_multiselect_option = ['BridgeWorld', 'Realm']
    collection_list = filter_collection_list(default_multiselect_option)
    
    if 'collection_list' not in st.session_state:
        st.session_state.collection_list = collection_list
    if 'cartridge_select_list' not in st.session_state:
        st.session_state.cartridge_select_list = cartridge_list
    if 'cartridge_multiselect_box' not in st.session_state:
        st.session_state.cartridge_multiselect_box = default_multiselect_option
    if 'collection_list' not in st.session_state:
        st.session_state.collection_list = filter_collection_list(default_multiselect_option)
    
    
    st.header('Cartridge Info')
    first_container = st.container()
    
    def cartridge_selected():
        # st.session_state.cartridge_multiselect_box = cartridge_select
        with cols[0]:
            st.write('result of cartridge callback')
            st.write(f'cartridge select list {st.session_state.cartridge_select_list} vs multibox_selected: {st.session_state.cartridge_multiselect_box}')
            mask = df_collections['cartridge'].isin(st.session_state.cartridge_multiselect_box)
        
            collection_list = np.array(df_collections['collection'][mask].values)
            st.write(collection_list)
            st.session_state.collection_list = collection_list
            st.write('result of cartridge callback')
    # def co
        
    with first_container:
        st.markdown("Use the dropdown box to select a specific cartridge or collection.")
        # st.selectbox(label='Select cartridge', options = collection_list)
        
        cols=st.columns((1,1))
        
        with cols[0]:
            st.write(st.session_state.cartridge_select)
            st.write(st.session_state.cartridge_multiselect_box)
            cartridge_select = st.multiselect('Select the Cartridges to filter by', options=st.session_state.cartridge_select_list, default=st.session_state.cartridge_multiselect_box, on_change=cartridge_selected, key='cartridge_multiselect_box')
            
        #     # cartridge_selectbox = st.selectbox(label='Select cartridge', options=cartridge_list)
            
            
        with cols[1]:
            collection_select = st.multiselect('Select the Collection to filter by', options = st.session_state.collection_list, key='collection_select')
            st.write(st.session_state.collection_list)
        #     # collection_selectbox = st.selectbox(label='Select collection', options=st.session_state.collection_list)
        #     # st.write('hello worrld')
        #     # collection_info = get_collection_info()
            
            
        #     # collection_info_list = np.array(collection_info['name'].values)
        #     # st.selectbox(label='Select cartridge', options = collection_info_list)
        #     # st.dataframe(collection_inf
        
    second_container = st.container()
    with second_container:
        st.image('https://app.rlm.land/_next/image?url=%2Fassets%2Fadventurers%2F8.jpeg&w=1080&q=75')
        st.write(st.session_state.collection_list)
        st.write(st.session_state.cartridge_multiselect_box)
    
    
    
    