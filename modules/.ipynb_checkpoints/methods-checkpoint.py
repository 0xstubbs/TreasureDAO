import requests
from dotenv import load_dotenv
import os
load_dotenv()
import pandas as pd
from shroomdk import ShroomDK


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

    FLIPSIDE_API_KEY = 'b0c0a74a-2d78-4276-b4aa-24e69b4668d1'
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
    order by tr.block_timestamp
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