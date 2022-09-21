import pandas as pd
import numpy as np
import requests
import streamlit as st

cartridge_images = {
    'Realm':'https://trove.treasure.lol/images/fetch/f_auto,c_limit,w_1920,q_auto/https://djmahssgw62sw.cloudfront.net/0/realm_cartridge3.jpg',
    'Bridgeworld': 'https://trove.treasure.lol/images/fetch/f_auto,c_limit,w_1920,q_auto/https://djmahssgw62sw.cloudfront.net/0/Trove_Banner_Bridgeworld2.jpg',
    'Battlefly' :'https://trove.treasure.lol/images/fetch/f_auto,c_limit,w_1920,q_auto/https://djmahssgw62sw.cloudfront.net/0/battlefly_cartridge.jpg',
    'LifeDAO': 'https://trove.treasure.lol/images/fetch/f_auto,c_limit,w_1920,q_auto/https://djmahssgw62sw.cloudfront.net/0/life_cartridge.jpg',
    'Smolverse' : 'https://trove.treasure.lol/images/fetch/f_auto,c_limit,w_1920,q_auto/https://djmahssgw62sw.cloudfront.net/0/smolverse_cartridge.jpg',
    'Knights of the Ether': 'https://trove.treasure.lol/images/fetch/f_auto,c_limit,w_1920,q_auto/https://djmahssgw62sw.cloudfront.net/0/KOTECartridge2.png',
    'Lost SamuRise':'https://trove.treasure.lol/images/fetch/f_auto,c_limit,w_1920,q_auto/https://djmahssgw62sw.cloudfront.net/0/lost_samurise_cartridge.jpg',
    'Peek-A-Boo!':'https://trove.treasure.lol/images/fetch/f_auto,c_limit,w_1920,q_auto/https://djmahssgw62sw.cloudfront.net/0/peek-a-boo_cartridge.jpg',
    'SmithyDAO':'https://trove.treasure.lol/images/fetch/f_auto,c_limit,w_1920,q_auto/https://djmahssgw62sw.cloudfront.net/0/smithydao_cartridge.jpg',
    'Tales of Elleria':'https://trove.treasure.lol/images/fetch/f_auto,c_limit,w_1920,q_auto/https://djmahssgw62sw.cloudfront.net/0/tales_of_elleria_cartridge.jpg',
    'The Lost Donkeys':'https://trove.treasure.lol/images/fetch/f_auto,c_limit,w_1920,q_auto/https://djmahssgw62sw.cloudfront.net/0/the_lost_donkeys_cartridge.jpg',
    'Toadstoolz':'https://trove.treasure.lol/images/fetch/f_auto,c_limit,w_1920,q_auto/https://djmahssgw62sw.cloudfront.net/0/toadstoolz_cartridge.jpg',
    'Treasure':'https://trove.treasure.lol/images/fetch/f_auto,c_limit,w_1920,q_auto/https://djmahssgw62sw.cloudfront.net/0/treasure_cartridge.jpg'
}
collection_images = {
    'Adventurers of the Void':'https://trove.treasure.lol/images/fetch/f_auto,c_limit,w_640,q_auto/https://djmahssgw62sw.cloudfront.net/0/AOV2.jpg',
    'Realm':'https://trove.treasure.lol/images/fetch/f_auto,c_limit,w_640,q_auto/https://djmahssgw62sw.cloudfront.net/0/realm_square_dark.jpg',
    'Realm - Collectibles':'https://trove.treasure.lol/images/fetch/f_auto,c_limit,w_640,q_auto/https://djmahssgw62sw.cloudfront.net/0/RealmCollectibles.jpg',
    
    
}