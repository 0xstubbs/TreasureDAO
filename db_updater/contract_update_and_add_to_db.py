import psycopg2 as pg2
from dotenv import load_dotenv
import os
import pandas as pd
import sqlalchemy
import requests
from datetime import date
import time

def get_all_contracts_latest_block():

    conn = pg2.connect(
        host= "database-2.c2bw3zzer4hr.us-west-1.rds.amazonaws.com",
        # host = "database-3.c2bw3zzer4hr.us-west-1.rds.amazonaws.com", 
        port = 5432,
        user = 'postgres',
        password = AWS_DB_PASSWORD,
        database = "magic_treasure_db"
        # database = "skycatcher_db"
    )

    cur = conn.cursor()

    ##Get the latest blocknumber so we can query alchemy more efficiently
    sql_query = """
    SELECT 
        contract_address as contract_address,
        cl.cartridge_name,
        cl.collection_name,
        max(blocknum)
        
    FROM erc721_transfers et
    left join contract_list cl on cl.contract_address = tt."rawContract.address" 
    group by 1,2,3
    """
    cur.execute(sql_query)

    data = cur.fetchall()

    cols = []
    for elt in cur.description:
        cols.append(elt[0])
        
    df = pd.DataFrame(data=data, columns = cols)
    # print(df)
    return df

def get_contract_latest_block(contract_address):

    conn = pg2.connect(
        host= "database-2.c2bw3zzer4hr.us-west-1.rds.amazonaws.com",
        # host = "database-3.c2bw3zzer4hr.us-west-1.rds.amazonaws.com",
        port = 5432,
        user = 'postgres',
        password = AWS_DB_PASSWORD,
        database = "magic_treasure_db"
        # database = "skycatcher_db"
    )

    cur = conn.cursor()

    ##Get the latest blocknumber so we can query alchemy more efficiently
    sql_query = f"""
    SELECT 
        max(blocknum) as latest_retrieved_block
        
    FROM erc721_transfers et
    """
    cur.execute(sql_query)

    data = cur.fetchone()

    # cols = []
    # for elt in cur.description:
    #     cols.append(elt[0])
        
    # df = pd.DataFrame(data=data, columns = cols)
    # print(df)
    if data[0] is None:
        return 0
    else:
        return data[0]
    # print(data)
    # return data


def get_response_wo_pagekey(contract_address, start_block, ALCHEMY_API_KEY_TREASURE):
  url = f"https://arb-mainnet.g.alchemy.com/v2/{ALCHEMY_API_KEY_TREASURE}"
  payload = {
      "id": 1,
      "jsonrpc": "2.0",
      "method": "alchemy_getAssetTransfers",
      "params": [
          {
              "fromBlock": f"{start_block}",
              "toBlock": "latest",
              "contractAddresses": [f"{contract_address}"],
              "category": ["erc20", "erc721", "erc1155"],
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

  response = requests.post(url, json=payload, headers=headers)
  if 'error' in response.json():
    print(response.json()['error'])
  else:
    try:
        response=response.json()['result']
    except:
        response=response.json()
        print(response.keys())
  # print(response.text)
    return response

def get_response_w_pgkey(ALCHEMY_API_KEY_TREASURE, start_block, contract_address, _page_key):
    url = f"https://arb-mainnet.g.alchemy.com/v2/{ALCHEMY_API_KEY_TREASURE}"
  # contract_address = "0x539bdE0d7Dbd336b79148AA742883198BBF60342"
    payload = {
      "id": 1,
      "jsonrpc": "2.0",
      "method": "alchemy_getAssetTransfers",
      "params": [
          {
              "fromBlock": f"{start_block}",
              "toBlock": "latest",
              "contractAddresses": [f"{contract_address}"],
              "category": ["erc20", "erc721", "erc1155"],
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
    response = requests.post(url, json=payload, headers=headers)
    try:
        response = response.json()['result']
        # print(response)
        return response
    except:
        print(f"didn't work!\n{response}")
        return response.json()

load_dotenv()
start_time = time.time()
####------------------------------------------------------------------------------------####
####                             Connect to DB                                          ####
####------------------------------------------------------------------------------------####
AWS_DB_PASSWORD = os.getenv("AWS_DB_PASSWORD")
ALCHEMY_API_KEY_TREASURE = os.getenv("ALCHEMY_API_KEY_TREASURE")


# contract_address = "0xfe8c1ac365ba6780aec5a985d989b327c27670a1"


# latest_retrieved_block = int(get_contract_latest_block(contract_address[0]))
# print(latest_retrieved_block)

# latest_block_hex = hex(latest_retrieved_block)

contract_list = ['0xfe8c1ac365ba6780aec5a985d989b327c27670a1', '0x6325439389e0797ab35752b4f43a14c004f22a9c', '0xd666d1cc3102cd03e07794a61e5f4333b4239f53',
                 '0xf6cc57c45ce730496b4d3df36b9a4e4c3a1b9754', '0x17dacad7975960833f374622fad08b90ed67d1b5', '0xae0d0c4cc3335fd49402781e406adf3f02d41bca',
                 '0xb16966dad2b5a5282b99846b23dcdf8c47b6132c', '0xdf32aed1eb841a174cb637eaa1707026319fb563', '0x0dccab3f2fc587b67bfdc66ffd2c87a567b21394',
                 '0x747910b74d2651a06563c3182838eae4120f4277', '0x4de95c1e202102e22e801590c51d7b979f167fbb', '0x8ec68f970e1c61b44b6d81c3b78ca931c6ffc92d', 
                 '0x8762dbd391fd90b29eccbb628cd54bd92f5fc1f3', '0x00000000016c35e3613ad3ed484aa48f161b67fd', '0xd666d1cc3102cd03e07794a61e5f4333b4239f53']
df_list = []
for contract in contract_list:
    latest_retrieved_block = int(get_contract_latest_block(contract))
    print(latest_retrieved_block)

    latest_block_hex = hex(latest_retrieved_block)
    
    print(f"Contract: {contract}")
    page_key = None
    concat_num=0
    skip_other_pages=False
    # df_transfers = pd.DataFrame()
    

    response_0 = get_response_wo_pagekey(contract, latest_block_hex,  ALCHEMY_API_KEY_TREASURE)
    print(response_0.keys())
    if 'pageKey' in response_0:
        page_key = response_0['pageKey']
    else:
        print('Not enough for second page')
        skip_other_pages = True
        df_temp = pd.json_normalize(response_0['transfers'])
    df_list.append(df_temp)
    # df_transfers = pd.concat([df_transfers, pd.json_normalize(response_0['transfers'])], axis=0)

    while True:
        if not skip_other_pages:
            response=get_response_w_pgkey(ALCHEMY_API_KEY_TREASURE, latest_block_hex, contract, page_key)
            # print(f"\n******************\nLength: {len(response['transfers'])}")
            if 'transfers' in response:
                
                df_new = pd.json_normalize(response['transfers'])
                df_list.append(df_new)
                # df_transfers = pd.concat([df_transfers, df_new], axis=0)
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
    df_transfers = pd.concat(df_list)
    # df_transfers=df_transfers.drop(['uniqueId', 'erc1155Metadata', 'value', 'erc721TokenId', 'rawContract.decimal', 'rawContract.value', 'category', 'asset'], axis=1)

def to_hex(x):
    # return int(hex(x))
    return int(x, base=16)

def lambda_handler(_df):
    df_transfers_numeric = _df
    # df_transfers.copy()
    df_transfers_numeric.loc[:, 'blockNum'] = df_transfers_numeric['blockNum'].apply(to_hex)
    # df_transfers_numeric.loc[:, 'erc721TokenId'] = df_transfers_numeric['erc721TokenId'].apply(to_hex)
    df_transfers_numeric.loc[:, 'tokenId'] = df_transfers_numeric['tokenId'].apply(to_hex)

    # df_transfers_numeric['value']= df_transfers_numeric['value'].fillna(1)
    df_transfers_numeric.rename(columns={'blockNum':'blocknum', 'tokenId':'tokenid', 'rawContract.address':'contract_address', 'metadata.blockTimestamp':'block_timestamp', 'from':'from_address', 'to':'to_address'}, inplace=True)
    df_transfers_numeric['block_timestamp'] = pd.to_datetime(df_transfers_numeric['block_timestamp']).dt.tz_convert(None)
    
    print(df_transfers_numeric.head())
    print(df_transfers_numeric.columns)
    print(df_transfers_numeric.info())
    
    
    # df_transfers_numeric.datetime.dt.tz_convert(None)
    df_transfers_numeric = df_transfers_numeric.drop(columns=['uniqueId', 'rawContract.value', 'rawContract.decimal', 'value', 'erc1155Metadata', 'asset', 'category', 'erc721TokenId'])
    print(df_transfers_numeric.head())
    print(df_transfers_numeric.columns)
    print(df_transfers_numeric.info())

    #Define connection variables for sqlalchemy connection
    host= "database-2.c2bw3zzer4hr.us-west-1.rds.amazonaws.com"
    # host = "database-3.c2bw3zzer4hr.us-west-1.rds.amazonaws.com"
    port = 5432
    user = 'postgres'
    password = AWS_DB_PASSWORD
    database = "magic_treasure_db"
    # database = "skycatcher_db"

    #Create the sqlalchemy connection and append the db
    postgres_str = f'postgresql://{user}:{password}@{host}:{port}/{database}'
    engine = sqlalchemy.create_engine(postgres_str)
    df_transfers_numeric.to_sql('erc721_transfers', con=engine, index=False, if_exists='append', chunksize=10000)

    ##Update the materialized view so that it contains the new info
    conn = pg2.connect(
        host= "database-2.c2bw3zzer4hr.us-west-1.rds.amazonaws.com",
        port = 5432,
        user = 'postgres',
        password = AWS_DB_PASSWORD,
        database = "magic_treasure_db"
    )
    cur = conn.cursor()

    sql_query = """
    REFRESH MATERIALIZED VIEW bridgeworld_daily_balances;
    """
    cur.execute(sql_query)
    cur.close()
    conn.close()
    
    print("This came from the code!!!")


lambda_handler(df_transfers)
