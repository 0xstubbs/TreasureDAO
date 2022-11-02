import psycopg2 as pg2
from dotenv import load_dotenv
import os
import pandas as pd
import sqlalchemy
import requests
from datetime import date
import time
import datetime

from sqlalchemy.types import Integer, Text, DateTime

def get_connection(AWS_DB_PASSWORD):
    print(f'entering get_connection w/ {AWS_DB_PASSWORD}')
    try:
        conn = pg2.connect(
            host= "database-2.c2bw3zzer4hr.us-west-1.rds.amazonaws.com",
            port = 5432,
            user = "postgres",
            password=AWS_DB_PASSWORD,
            database = "magic_treasure_db"
        )
        print('successful connection')
    except Exception as e:
        print("Unable to connect to database...")
        raise e
    return conn

def get_magic_transfers_latest_block(AWS_DB_PASSWORD):
    try:
        connection = get_connection(AWS_DB_PASSWORD)
        with connection as conn:
            cur = conn.cursor()

            ##Get the latest blocknumber so we can query alchemy more efficiently
            sql_query = f"""
            SELECT 
                max(block_number) as latest_retrieved_block
            FROM raw_magic_token_transfers mt
            """
            cur.execute(sql_query)

            data = cur.fetchone()
    except Exception as e:
        print("Error while connecting to pgsql")
        data is None
    finally:
        if data is None:
            return int(0)
        else:
            return int(data[0])
    
def get_response_wo_pagekey(start_block, ALCHEMY_API_KEY_TREASURE):
    url = f"https://arb-mainnet.g.alchemy.com/v2/{ALCHEMY_API_KEY_TREASURE}"
    payload = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "alchemy_getAssetTransfers",
        "params": [
            {
                "fromBlock": f"{start_block}",
                "toBlock": "latest",
                "contractAddresses": ["0x539bde0d7dbd336b79148aa742883198bbf60342"],
                "category": ["erc20"],
                "withMetadata": True,
                "excludeZeroValue": False,
                "maxCount": "0x3e8",
                "order": "asc"
            }
        ]
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    print('Attempting to get response...')
    try:
        response = requests.post(url, json=payload, headers=headers)
    except requests.exceptions.RequestException as e:
        print('Request exception....')
        raise e
    else:
        response=response.json()['result']
    print("Returning response...")
    return response

def get_response_w_pgkey(ALCHEMY_API_KEY_TREASURE, start_block, _page_key):
    url = f"https://arb-mainnet.g.alchemy.com/v2/{ALCHEMY_API_KEY_TREASURE}"
  # contract_address = "0x539bde0d7dbd336b79148aa742883198bbf60342"
    payload = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "alchemy_getAssetTransfers",
        "params": [
            {
                "fromBlock": f"{start_block}",
                "toBlock": "latest",
                "contractAddresses": ["0x539bde0d7dbd336b79148aa742883198bbf60342"],
                "category": ["erc20"],
                "withMetadata": True,
                "excludeZeroValue": False,
                "maxCount": "0x3e8",
                "order": "asc",
                "pageKey": f"{_page_key}"
            }
        ]
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    print("Attempting to get response...")
    try:
        response = requests.post(url, json=payload, headers=headers)
    except requests.exceptions.RequestException as e:
        print("Exception thrown when instantiating response object...")
    else:
        response = response.json()['result']
        
    finally:
        print("Returning response json object...")
        return response

def to_hex(x):
    return int(x, base=16)

def get_sqlalchemy_engine(AWS_DB_PASSWORD):
    host= "database-2.c2bw3zzer4hr.us-west-1.rds.amazonaws.com"
    port = 5432
    user = 'postgres'
    password = AWS_DB_PASSWORD
    database = "magic_treasure_db"
    
    postgres_str = f"postgresql://{user}:{password}@{host}:{port}/{database}"
    try:
        engine = sqlalchemy.create_engine(postgres_str)
    except Exception as e:
        print('engine could not be created')
        print(e)
        raise e
    else:
        print('returning engine')
        return engine

def update_magic():
    load_dotenv()
    start_time = time.time()
    # ####------------------------------------------------------------------------------------####
    # ####                             Connect to DB                                          ####
    # ####------------------------------------------------------------------------------------####
    # AWS_DB_PASSWORD = os.getenv("AWS_DB_PASSWORD")
    # ALCHEMY_API_KEY_TREASURE = os.getenv("ALCHEMY_API_KEY_TREASURE")
    print('Updating magic_transfers from client NOT lambda')
    
    AWS_DB_PASSWORD = os.environ["AWS_DB_PASSWORD"]
    ALCHEMY_API_KEY_TREASURE = os.environ["ALCHEMY_API_KEY_TREASURE"]
    
    latest_retrieved_block = get_magic_transfers_latest_block(AWS_DB_PASSWORD)

    latest_block_hex = hex(latest_retrieved_block)

    print("Contract: 0x539bde0d7dbd336b79148aa742883198bbf60342")
    page_key=None
    concat_num=0
    skip_other_pages=False
    df_transfers = pd.DataFrame()

    response_0 = get_response_wo_pagekey(latest_block_hex,  ALCHEMY_API_KEY_TREASURE)
    print(response_0.keys())
    if 'pageKey' in response_0:
        page_key=response_0['pageKey']
    else:
        print('Not enough for second page')
        skip_other_pages = True
    df_transfers = pd.concat([df_transfers, pd.json_normalize(response_0['transfers'])], axis=0)

    while True:
        if not skip_other_pages:
            response=get_response_w_pgkey(ALCHEMY_API_KEY_TREASURE, latest_block_hex, page_key)
            if 'transfers' in response:
                
                df_new = pd.json_normalize(response['transfers'])
                df_transfers = pd.concat([df_transfers, df_new], axis=0)
            else:
                break
            try:
                page_key=response['pageKey']
            except:
                break

            concat_num = concat_num + 1
            if concat_num % 100 == 0:
                print(f"Iteration Number: {concat_num}")
            # print(page_key)
        else:
            break
    # df_transfers=df_transfers.drop(['uniqueId', 'tokenId', 'erc1155Metadata', 'erc721TokenId', 'rawContract.decimal', 'rawContract.value', 'category', 'asset'], axis=1)
    df_transfers=df_transfers.drop(['tokenId', 'erc1155Metadata', 'erc721TokenId', 'rawContract.decimal', 'rawContract.value', 'category', 'asset'], axis=1)
        
    df_transfers_numeric = df_transfers.copy()
    df_transfers_numeric.loc[:, 'blockNum'] = df_transfers_numeric['blockNum'].apply(to_hex)

    df_transfers_numeric.rename(columns={'blockNum':'block_number', 'rawContract.address':'contract_address', 'metadata.blockTimestamp':'block_timestamp', 'from':'sender', 'to':'receiver'}, inplace=True)
    df_transfers_numeric['block_timestamp'] = pd.to_datetime(df_transfers_numeric['block_timestamp']).dt.tz_convert(None)
    
    current_datetime = datetime.datetime.now()
    current_datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    df_transfers_numeric.loc[:, 'upload_datetime'] = current_datetime_str
    
    engine = get_sqlalchemy_engine(AWS_DB_PASSWORD)
    with engine.begin() as conn:
        print("Trying to append magic_transfers db with chunksize of 5000")
        df_transfers_numeric.to_sql('raw_magic_token_transfers', con=conn, index=False, if_exists='append', chunksize=5000, 
                                    dtype={
                                    "unique_id":Text,
                                    "block_number": sqlalchemy.INTEGER,
                                    "block_timestamp":DateTime,
                                    "hash":Text,
                                    "contract_address":Text,
                                    "sender":Text,
                                    "receiver":Text,
                                    "value":sqlalchemy.Float,
                                    "upload_datetime":Text
                                })
    print('Successfully updated magic token transfers...')
load_dotenv()
start_time = time.time()
####------------------------------------------------------------------------------------####
####                             Connect to DB                                          ####
####------------------------------------------------------------------------------------####
AWS_DB_PASSWORD = os.getenv("AWS_DB_PASSWORD")
ALCHEMY_API_KEY_TREASURE = os.getenv("ALCHEMY_API_KEY_TREASURE")    
update_magic()
end_time = time.time()

print(f"Gathering and uploading magic transfers took {end_time-start_time} seconds")