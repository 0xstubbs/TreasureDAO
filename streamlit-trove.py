import streamlit as st
import pandas as pd
import sys

import modules.thegraph as thegraph




st.set_page_config(layout='wide')
pd.set_option('display.precision', 2)
st.image('https://skycatcher.xyz/images/logo-white.svg')

tab1, tab2, tab3 = st.tabs(['Magic Token', 'Legion', 'Trove'])

with tab3:
    st.header('Trove Marketplace')
    with st.expander(' '):
        cartridge_category=['All', 'Core', 'Partner']
        selected_category = st.radio(
        "Cartridge Category",
        cartridge_category)
        cartridges = ['Bridgeworld', 'Smolverse']

        if selected_category == 'Core':
            cartridges = ['Bridgeworld', 'Smolverse']
            st.write('You selected Core.')
            st.write(cartridges)
        elif selected_category == 'Partner':
            cartridges = ['BattleFly', 'Knights of the Ether', 'LifeDAO', 'Realm', 'SmithyDAO', 'Tales of Elleria', 'The Lost Donkeys', 'Toadstoolz']
            st.write("You selected Partner.")
            st.write(cartridges)
        else:
            cartridges = ['Bridgeworld', 'Smolverse', 'BattleFly', 'Knights of the Ether', 'LifeDAO', 'Realm', 'SmithyDAO', 'Tales of Elleria', 'The Lost Donkeys', 'Toadstoolz']
            st.write("You selected all.")
        
        collections = thegraph.get_collections(selected_category)
        collections = collections[collections['contract'] == collections['id']].sort_values('name', ascending=True)
        
        option = st.selectbox(
        'Select Cartidge...',
        cartridges)
    