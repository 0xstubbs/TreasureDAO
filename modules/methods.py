import requests
from dotenv import load_dotenv
import os
load_dotenv()
import pandas as pd
from shroomdk import ShroomDK
from datetime import date
import numpy as np


ALCHEMY_API_KEY_TREASURE = os.getenv('ALCHEMY_API_KEY_TREASURE')
def alchemy_getTokenBalances(contract_address):
    url = f'https://arb-mainnet.alchemyapi.io/v2/{ALCHEMY_API_KEY_TREASURE}'
    
    headers = {
    "accept": "application/json",
    "content-type": "application/json"
    }

    response = requests.post(url, headers=headers)

    print(response.text)
    response = requests.get(url).json()['result']
    
    df = pd.json_normalize(response,
                           record_path='tokenBalances')
    
def get_magicTradingVolume():
    os.getenv('FLIPSIDE_API_KEY')
    FLIPSIDE_API_KEY = 'b0c0a74a-2d78-4276-b4aa-24e69b4668d1'
    page_num = 1
    pg_size = 100000
    sdk = ShroomDK(FLIPSIDE_API_KEY)

    sql_query = """
    select 
    block_timestamp,
    block_number,
    -- tx_hash,
    origin_from_address,
    -- origin_to_address,
    symbol_in,
    amount_in, 
    amount_in_usd,
    symbol_out,
    amount_out,
    amount_out_usd
    from arbitrum.sushi.ez_swaps sw
    where contract_address = lower('0xB7E50106A5bd3Cf21AF210A755F9C8740890A8c9')
    order by block_timestamp asc
    """

    page_num=1
    full_queries = True
    df=pd.DataFrame()

    while full_queries is True:

        query_result_set = sdk.query(
            sql_query,
            ttl_minutes=60,
            cached=True,
            timeout_minutes=20,
            retry_interval_seconds=1,
            page_size=pg_size,
            page_number=page_num
        )
        
        if query_result_set.run_stats.record_count > 0:
        
            df_new = pd.json_normalize(query_result_set.records)
            df = pd.concat([df, df_new], axis=0)
            page_num = page_num + 1
        else:
            full_queries = False
            break
        
    return df

def get_magicTransfers():
    import pandas as pd
    import requests
    from shroomdk import ShroomDK
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    FLIPSIDE_API_KEY=os.getenv("FLIPSIDE_API_KEY")

    
    page_num = 1
    pg_size = 100000
    sdk = ShroomDK(FLIPSIDE_API_KEY)

    sql_query = """
    Select
        tr.block_timestamp,
    tx_hash,
    origin_from_address,
    to_address,
    'MAGIC' as symbol,
    raw_amount/pow(10,18) as amount

    from arbitrum.core.fact_token_transfers tr
    where tr.contract_address = lower('0x539bdE0d7Dbd336b79148AA742883198BBF60342')
    order by tr.block_timestamp desc
    """

    page_num=1
    full_queries = True
    df=pd.DataFrame()

    while full_queries is True:

        query_result_set = sdk.query(
            sql_query,
            ttl_minutes=60,
            cached=True,
            timeout_minutes=20,
            retry_interval_seconds=1,
            page_size=pg_size,
            page_number=page_num
        )
        
        if query_result_set.run_stats.record_count > 0:
        
            df_new = pd.json_normalize(query_result_set.records)
            df = pd.concat([df, df_new], axis=0)
            page_num = page_num + 1
        else:
            full_queries = False
            break
    return df

# def activity_filterDateAndTxns(_df, date_list, tx_min_list):
#     print("###---------------------------------------------------------####")
#     print("###---------------------------------------------------------####\nMethod: activity_filterDateAndTxns")
#     print('This method returns an n by m matrix with the number of active wallets given a time restriction and minimum # of txns')
    
#     # 
#     if _df == 'Get New':
#         df = get_magicTransfers()
#     else:
#         df = _df
        
#     god = dict()
    
#     df['date'] = pd.to_datetime(df['block_timestamp']).dt.date
#     df_test = df[['date', 'tx_hash', 'origin_from_address', 'amount']]
    
# #     dm_list = []
# #     for date_item in date_list:
# #         filter_time = date_item
# #         date_mask = df_test['date'] > date.today() - pd.Timedelta(days=filter_time)
# #         dft_date = df_test[date_mask].groupby('origin_from_address')['tx_hash'].count().reset_index()
        
# #         interactions_date_filtered = {date_item:dft_date}
        
# #         dm_list.append(dft_date)
        
# #         num_active_list = {}
        
# #     for tx_min in tx_min_list:
# #         for k in interactions_date_filtered:
# #             dm=interactions_date_filtered[k]
# #             tx_min_filter = dm['tx_hash'] >= tx_min
# #             active_accounts = dft_date[tx_min_filter].sort_values('tx_hash', ascending=False)
# #             num_active = len(set(active_accounts['origin_from_address'].values))
            
# #             god.update({(k, tx_min) : {'min_txns': tx_min, 'timeframe': k, 'num_active':num_active}})
            
# #     return god

# # def activity_filterDateAndTxns(_df, date_list, tx_min_list):
# def activity_filterDateAndTxns(_df, date_list, tx_min_list):
#     # 
#     if (type(_df) == str):
#         df = get_magicTransfers()
#     else:
#         df = _df
#     interactions_date_filtered = dict()    
#     god = dict()
    
#     df['date'] = pd.to_datetime(df['block_timestamp']).dt.date
#     df_test = df[['date', 'tx_hash', 'origin_from_address', 'amount']]
    
#     dm_list = []
#     for date_item in date_list:
#         dft=pd.DataFrame()
#         filter_time = date_item
#         date_mask = df_test['date'] > date.today() - pd.Timedelta(days=filter_time)
#         dft_date = df_test[date_mask].copy()
        
#         dft=dft_date.groupby('origin_from_address')['tx_hash'].count().reset_index()
        
#         interactions_date_filtered.update({date_item:dft})
        
        
#         num_active_list = {}
        
#     for tx_min in tx_min_list:
#         print(f'---------------------Min # Txns: {tx_min}------------------\n')
#         for k in interactions_date_filtered:
#             print(f'# Days:{k}\nMin Txns:{tx_min}------------------\n')
#             dm=interactions_date_filtered[k]
#             tx_min_filter = dm['tx_hash'] >= tx_min
#             active_accounts = dm[tx_min_filter]
#             num_active = len(set(active_accounts['origin_from_address'].values))
            
#             # print(f'Updating god with: {k} and {tx_min}')
#             god.update({(k, tx_min) : {'min_txns': tx_min, 'timeframe': k, 'num_active':num_active, 'dataframe':active_accounts}})
#     print('We have god!')
#     print(god)
    
#     df = pd.DataFrame.from_dict(god).T
#     return god

def activity_filteredByDateAndTxns(_df, date_list, tx_min_list):
    # 
    if type(_df) == str:
        df = get_magicTransfers()
    else:
        df = _df
    interactions_date_filtered = dict()    
    god = dict()
    
    df['date'] = pd.to_datetime(df['block_timestamp']).dt.date
    df_test = df[['date', 'tx_hash', 'origin_from_address', 'amount']]
    
    dm_list = []
    for date_item in date_list:
        dft=pd.DataFrame()
        filter_time = date_item
        date_mask = df_test['date'] > date.today() - pd.Timedelta(days=filter_time)
        dft_date = df_test[date_mask].copy()
        
        dft=dft_date.groupby('origin_from_address')['tx_hash'].count().reset_index()
        
        dft['interval_filter']=date_item
        
        for tx_min in tx_min_list:
            mask = dft['tx_hash']>=tx_min
            masked_df =dft[mask]
            
            address_list = np.array(((masked_df['origin_from_address'].unique())))
            num_active = len(address_list)
            
            god.update({(tx_min, date_item) : {'num_active': num_active, 'addresses': address_list}})
    
    return pd.DataFrame(god).T