import pandas as pd
import numpy as np
import requests
import time

def get_magic_sinks():
    url = "https://api.thegraph.com/subgraphs/name/wyze/treasure-sinks"
    query = """{
    sinks {
        id
        name
        tokens{
        name
        quantity
        tokenId
        }
    }
    }
    """
    response = requests.post(url, json={'query':query}).json()['data']['sinks']

    df_sink = pd.json_normalize(response
                  # , "id", "name", ["id", "name", "quantity", "tokenid"]
                , record_path='tokens'
                , meta= ['id', 'name']
                , record_prefix="token."
                , meta_prefix = "sink."
                 )[['sink.id', 'sink.name', 'token.name', 'token.quantity', 'token.tokenId']]
    
    return df_sink

def get_magic_eth_price():
    magic_url_daily='https://api.coingecko.com/api/v3/coins/ethereum/contract/0xb0c7a3ba49c7a6eaba6cd4a96c55a1391070ac9a/market_chart/?vs_currency=usd&days=max'
    magic_url_hourly='https://api.coingecko.com/api/v3/coins/magic/market_chart?vs_currency=usd&days=90&interval=hourly'
    weth_url_daily='https://api.coingecko.com/api/v3/coins/ethereum/contract/0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2/market_chart/?vs_currency=usd&days=max'
    weth_url_hourly='https://api.coingecko.com/api/v3/coins/ethereum/market_chart?vs_currency=usd&days=90&interval=hourly'
    df = pd.DataFrame()

    magic_dict = {
        'magic_daily' : {'url': magic_url_daily,  'contract_address': "0xb0c7a3ba49c7a6eaba6cd4a96c55a1391070ac9a", 'name': 'MAGIC'},
        'magic_hourly': {'url': magic_url_hourly, 'contract_address': "0xb0c7a3ba49c7a6eaba6cd4a96c55a1391070ac9a", 'name': 'MAGIC'},
        'weth_daily'  : {'url': weth_url_daily,   'contract_address': "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", 'name': 'WETH'},
        'weth_hourly' : {'url': weth_url_hourly,  'contract_address': "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", 'name': 'WETH'}
    }

    for k in magic_dict:
        # print(magic_dict[k], k)
        url = magic_dict[k]['url']
        contract_address = magic_dict[k]['contract_address']
        name = magic_dict[k]['name']
        
        response = requests.get(url)
        if response.status_code == 200:
            response=response.json()
            for v in response:
        
                new_df = pd.DataFrame(response[v])
                new_df['type']=v
                new_df['name']=name
                new_df['contract_address'] = contract_address
                
                df = pd.concat([df, new_df], axis=0)
        else: 
            break
            
    df=df.rename(columns={0: 'timestamp', 1:'price'})        
    df['datetime']=pd.to_datetime(df['timestamp'], unit='ms').dt.strftime('%Y-%m-%d %H')
    df['date']=pd.to_datetime(df['timestamp'], unit='ms').dt.date
    

    df=df[['timestamp', 'datetime', 'date', 'price', 'type', 'name', 'contract_address']]
    min_date_magic = (df[df['name']=='MAGIC'])['date'].min()

    df_magic_mask = df['date'] >= min_date_magic
    df_magic_timeline=df.loc[df_magic_mask]
    
    df_magic_timeline =df_magic_timeline.groupby(['datetime','date', 'type', 'name'])['price'].mean().reset_index()
    
    df_comp_weth = df[(df['name'] =='WETH') & (df['type'] == 'prices')][['datetime', 'date', 'price', 'name']]
    df_comp_magic = df[(df['name'] =='MAGIC') & (df['type'] == 'prices')][['datetime', 'date', 'price', 'name']]
    
    df_comp_weth = df[(df['name'] =='WETH') & (df['type'] == 'prices')][['datetime', 'date', 'price', 'name']]
    df_comp_weth['usd/weth'] = df_comp_weth['price']
    df_comp_magic = df[(df['name'] =='MAGIC') & (df['type'] == 'prices')][['datetime', 'date', 'price', 'name']]
    df_comp_magic['usd/magic'] = df_comp_magic['price']
    
    df_comp_merge = df_comp_weth.merge(df_comp_magic, how='left', left_on=['datetime'], right_on=['datetime']).dropna()
    df_comp_merge['eth/magic'] = df_comp_merge.loc[:,'price_y']/df_comp_merge.loc[:,'price_x']
    df_comp_merge['magic/eth'] = df_comp_merge.loc[:,'price_x']/df_comp_merge.loc[:,'price_y']
    df_comp_merge['weth/usd'] = 1/df_comp_merge.loc[:, 'price_x']

    df_comp_merge = df_comp_merge.rename(columns={'date_x':'date'})
    df_comp_merge = df_comp_merge.sort_values('datetime', ascending=True).reset_index()
    print(df_comp_merge)
    
    print(df_comp_merge.columns)
    return df_comp_merge