###This is the lambda function that updates magic_transfers
###Updated 22-11-01

import psycopg2 as pg2
from dotenv import load_dotenv
import os
import pandas as pd
import sqlalchemy
import requests
from datetime import date
import time
import json

import boto3
from botocore.session import Session
from botocore.config import Config
import base64
from botocore.exceptions import ClientError

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

region_name="us-west-1"

config = Config(
    read_timeout=900,
    connect_timeout=900,
    retries={'max_attempts':0})
    
print('set up the session and client')
#Set up the session and client
boto3.set_stream_logger('')
print("""
****************************************************
Creating boto3 Session and clients.
****************************************************
""")

session = boto3.session.Session()
client1 = session.client(
        service_name='secretsmanager',
        region_name='us-west-1',
        config=config
        )
client2 = session.client(
        service_name='secretsmanager',
        region_name='us-west-1',
        config=config
        )

def get_secret(_selected_secret):
    print(f"in get_secret w/ selected secret: {_selected_secret}")
    secret_name_dict = {
        'db_password':'AWS_DB_PASSWORD',
        "alchemy_api":"ALCHEMY_API_KEY_TREASURE"
        }
    secret_name = secret_name_dict[_selected_secret]

    region_name = "us-west-1"
    print(f'secret name: {secret_name}')
    print(f'region name: {region_name}')
    
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )

    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        else:
            raise e
            # Decrypts secret using the associated KMS key.
            # Depending on whether the secret is a string or binary, one of these fields will be populated.
    
    secret = get_secret_value_response['SecretString']
    print(f"we have the secret: {secret}")
    secret_dict = eval(secret)
    print(secret_dict)
    return secret_dict

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
    print('get_magic_transfers_latest_block')
    try:
        print('establishing connection')
        conn = get_connection(AWS_DB_PASSWORD)

        cur = conn.cursor()
        print('got cursor')

        sql_query = f"""SELECT max(block_number) as latest_retrieved_block FROM magic_transfers mt"""
        print(sql_query)
        cur.execute(sql_query)
        data = cur.fetchone()
        print(data)
    except (Exception, Error) as error:
        print("Error while connecting to pgsql", error)
        data is None
    finally:
        cur.close()
        conn.close()
    if data[0] is None:
        return int(0)
    else:
        return int(data[0])
        
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

def get_contract_latest_block(contract_address, AWS_DB_PASSWORD):
    print('in get_contract_latest_block')
    print(f'contract address: {contract_address}')
    print(f'AWS_DB_PASSWORD: {AWS_DB_PASSWORD}')
    try:
        conn=get_connection(AWS_DB_PASSWORD)
        print (f'got connection: {conn}')
        cur = conn.cursor()
        print('get latest blocknumber so we can query alchemy better')
        ##Get the latest blocknumber so we can query alchemy more efficiently
        sql_query = f"""
            SELECT 
            max(blocknum) as latest_retrieved_block
            FROM erc721_transfers et
            """
        print(f'sql_query: {sql_query}')
        cur.execute(sql_query)
    except Exception as e:
        print(e)
    else:
        print('get data')
        data = cur.fetchone()
        print(f'data is {data}')
    finally:
        cur.close()
        conn.close()
        
    if data[0] is None:
        print(f'data[0] is None -- {data[0]}')
        return 0
    else:
        print(f'data[0] is: {data[0]}')
        return data[0]

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
    print('try for response')
    try:
        response = requests.post(url, json=payload, headers=headers)
    except requests.exceptions.RequestException as e:
        raise e
    print(response.text)
    if 'error' in response.json():
        print(response.json()['error'])
    else:
        try:
            response=response.json()['result']
        except:
            response=response.json()
        print(response.keys())
    print(f"returning response: {response}")
    return response

def get_response_w_pgkey(ALCHEMY_API_KEY_TREASURE, start_block, contract_address, _page_key):
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
        return response
    except:
        print(f"didn't work!\n{response}")
        return response

def to_hex(x):
    return int(x, base=16)



def lambda_handler(event, context):
    print('starting lambda handler')
    start_time = time.time()
    print("""
    ####------------------------------------------------------------------------------------####
    ####                             Connect to DB                                          ####
    ####------------------------------------------------------------------------------------####          
    """)
    print('Getting DB Credentials...')
    AWS_DB_CREDENTIALS=client1.get_secret_value(SecretId='AWS_DB_PASSWORD')['SecretString']
    AWS_DB_CREDENTIALS_DICT=eval(AWS_DB_CREDENTIALS)
    
    print('Getting API Credentials...')
    ALCHEMY_API_KEY_TREASURE=client2.get_secret_value(SecretId='ALCHEMY_API_KEY_TREASURE')['SecretString']
    ALCHEMY_API_KEY_SECRET_RESPONSE=eval(ALCHEMY_API_KEY_TREASURE)
    
    AWS_DB_PASSWORD = AWS_DB_CREDENTIALS_DICT['password']
    ALCHEMY_API_KEY = ALCHEMY_API_KEY_SECRET_RESPONSE['ALCHEMY_API_KEY_TREASURE']
    
    print("\n\n***********************************************")

    # contract_address = "0xfe8c1ac365ba6780aec5a985d989b327c27670a1" ##legion
    contract_address = "0x539bde0d7dbd336b79148aa742883198bbf60342" ##MAGIC
    
    print("""
    ####------------------------------------------------------------------------------------####
    ####                              Getting Latest Block                                  ####
    ####------------------------------------------------------------------------------------####          
    """)
    print("going into latest_retrieved_block")
    
    latest_retrieved_block = int(get_magic_transfers_latest_block(AWS_DB_PASSWORD))
    latest_block_hex = hex(latest_retrieved_block)

    print(latest_block_hex)

    print(f"Contract: {contract_address}")
    
    page_key = None
    concat_num=0
    skip_other_pages=False
    df_transfers = pd.DataFrame()
    df_list = []
    
    print("Getting the first response from Alchemy w/o a page key...")
    try:
        response_0 = get_response_wo_pagekey(contract_address, latest_block_hex, ALCHEMY_API_KEY)

        print("Checking if there are additional pages...")
        if 'pageKey' in response_0:
            page_key = response_0['pageKey']
            skip_other_pages=False
            print(f'Retreived page key: {page_key}')
        else:
            print('There were no additional pages...')
            skip_other_pages = True
        df_transfers = pd.concat([df_transfers, pd.json_normalize(response_0['transfers'])])
        df_list.append(pd.json_normalize(response_0['transfers']))
        print(f"length of df_list: {len(df_list)}")
    except:
        print("Unable to get a response for transfers w/o page key...")
        skip_other_pages=True
        
    # df_transfers = pd.concat([df_transfers, pd.json_normalize(response_0['transfers'])])
    # df_list.append(pd.json_normalize(response_0['transfers']))
    # print(f"length of df_list: {len(df_list)}")


    while not skip_other_pages:
        print("There are additional pages entries -- use get_response_w_pagekey()")
        try:
            response=get_response_w_pgkey(ALCHEMY_API_KEY, latest_block_hex, contract_address, page_key)
            print('Response received...')
            if 'transfers' in response:
                df_new = pd.json_normalize(response['transfers'])
                df_list.append(df_new)
                df_transfers = pd.concat([df_transfers, df_new], axis=0)
                print(f"Last 3 entries: {df_transfers.tail(3)}")
            else:
                print("\'transfers\' was not found in the response, breaking loop...")
                skip_other_pages=True
                # break
        except Exception as e:
            print("An exception was raised when trying to get response from alchemy...")
            raise e
            break
        else:
            try:
                print("Getting page key from response...")
                page_key=response['pageKey']
            except:
                print('Couldn\'t get a page key from response, will exit loop...')
                skip_other_pages=True
        finally:        
            concat_num = concat_num + 1
            if concat_num % 5 == 0:
                print(f"Iteration Number: {concat_num}")
    print("All transfers have been gathered.\nTransform data for upload to database...")        

    print(df_transfers.columns)
    df_transfers=df_transfers.drop(['uniqueId', 'tokenId', 'erc1155Metadata', 'erc721TokenId', 'rawContract.decimal', 'rawContract.value', 'category', 'asset'], axis=1)

    df_transfers_numeric = df_transfers.copy()
    df_transfers_numeric.loc[:, 'blockNum'] = df_transfers_numeric['blockNum'].apply(to_hex)
    df_transfers_numeric.rename(columns={'blockNum':'block_number', 'rawContract.address':'contract_address', 'metadata.blockTimestamp':'block_timestamp', 'from':'from_address', 'to':'to_address'}, inplace=True)
    df_transfers_numeric['block_timestamp'] = pd.to_datetime(df_transfers_numeric['block_timestamp']).dt.tz_convert(None)
    
    print('Creating an SQLAlchemy engine to connect to DB...')
    engine = get_sqlalchemy_engine(AWS_DB_PASSWORD)
    with engine.connect() as conn:
        print("Starting data upload...")
        df_transfers_numeric.to_sql('magic_transfers', con=engine, index=False, if_exists='append', chunksize=10000)
        print("Data upload complete...")
    
    print("""
*****************************************************************************************      
                Data has been gathered, transformed, and uploaded successfully.
*****************************************************************************************
""")
    return "Update complete. Exiting..."