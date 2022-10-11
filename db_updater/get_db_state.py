import psycopg2 as pg2
from dotenv import load_dotenv
import os
import pandas as pd
import sqlalchemy
# from .. import transfers_by_contract as tbc
import requests
from datetime import date
import time

load_dotenv()
start_time = time.time()
####------------------------------------------------------------------------------------####
####                             Connect to DB                                          ####
####------------------------------------------------------------------------------------####
AWS_DB_PASSWORD = os.getenv("AWS_DB_PASSWORD")
ALCHEMY_API_KEY_TREASURE = os.getenv("ALCHEMY_API_KEY_TREASURE")


def get_all_contracts_latest_block():

    conn = pg2.connect(
        host= "database-2.c2bw3zzer4hr.us-west-1.rds.amazonaws.com",
        port = 5432,
        user = 'postgres',
        password = AWS_DB_PASSWORD,
        database = "magic_treasure_db"
    )

    cur = conn.cursor()

    ##Get the latest blocknumber so we can query alchemy more efficiently
    sql_query = """
    SELECT 
        "rawContract.address" as contract_address,
        cl.cartridge_name,
        cl.collection_name,
        max(blocknum)
        
    FROM token_transfers tt
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
        port = 5432,
        user = 'postgres',
        password = AWS_DB_PASSWORD,
        database = "magic_treasure_db"
    )

    cur = conn.cursor()

    ##Get the latest blocknumber so we can query alchemy more efficiently
    sql_query = f"""
    SELECT 
        "rawContract.address" as contract_address,
        cl.cartridge_name,
        cl.collection_name,
        max(blocknum) as latest_retrieved_block
        
    FROM token_transfers tt
    left join contract_list cl on cl.contract_address = tt."rawContract.address"
    where tt."rawContract.address" = '{contract_address}'
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




contract_address = "0xfe8c1ac365ba6780aec5a985d989b327c27670a1"

latest_retrieved_block = int(get_contract_latest_block(contract_address)['latest_retrieved_block'].values)
latest_block_hex = hex(latest_retrieved_block)

contract_list = [contract_address]


print(f"Contract: {contract_address}")
page_key = None
concat_num=0
skip_other_pages=False
df_transfers = pd.DataFrame()

response_0 = get_response_wo_pagekey(contract_address, latest_block_hex,  ALCHEMY_API_KEY_TREASURE)
print(response_0.keys())
if 'pageKey' in response_0:
    page_key = response_0['pageKey']
else:
    print('Not enough for second page')
    skip_other_pages = True
df_transfers = pd.concat([df_transfers, pd.json_normalize(response_0['transfers'])], axis=0)

while True:
    if not skip_other_pages:
        response=get_response_w_pgkey(ALCHEMY_API_KEY_TREASURE, latest_block_hex, contract_address, page_key)
        print(f"\n******************\nLength: {len(response['transfers'])}")
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
        if concat_num % 10 == 0:
            print(f"Iteration Number: {concat_num}")
        print(page_key)
    else:
        break
df_transfers=df_transfers.drop(['uniqueId', 'erc1155Metadata'], axis=1)
# df_transfers.to_csv(f'{date.today()}_df_transfers_{contract_address}.csv')
# df_transfers.to_csv(f'df_transfers_{contract_address}.csv')


# df_transfers = pd.read_csv('/home/stubbs/Documents/skycatcher/TreasureDAO/df_transfers.csv' 
#                           , usecols=['hash', 'from', 'to', 'value', 'rawContract.address', 'metadata.blockTimestamp']
#                             , parse_dates=['metadata.blockTimestamp']
#                           )


#Split the raw data into two dataframes; 1. transfers out, 2. transfers in

#---------------------------------------------Create a 'transfers_out' dataframe-------------------------------#
#The values in the 'transfers_out' dataframe will be multiplied by -1.0 to show that the wallet balance is going down
df_transfers_out = df_transfers[['hash', 'from', 'value', 'metadata.blockTimestamp']].copy()
df_transfers_out['value']=df_transfers_out['value']*-1.0
df_transfers_out.rename(columns = {'hash': 'tx_hash', 'from':'address', 'value':'amount', 'metadata.blockTimestamp':'tx_timestamp'}, inplace=True)

#---------------------------------------------Create a 'transfers_in' dataframe-------------------------------#
#The values in 'transfers_in' are positive
df_transfers_in = df_transfers[['hash', 'to', 'value', 'metadata.blockTimestamp']].copy()
df_transfers_in.rename(columns = {'hash': 'tx_hash', 'to':'address', 'value':'amount', 'metadata.blockTimestamp':'tx_timestamp'}, inplace=True)

#-----------------------------Use Pandas concat to combine the 'in' and 'out' dataframes------------------------------#
transfers_all=pd.concat([df_transfers_in, df_transfers_out], axis=0)

#Create a 'date' column we will not be looking at individual txns. 
transfers_all['date'] = pd.to_datetime(transfers_all['tx_timestamp']).dt.date
# transfers_all = transfers_all[['date', 'tx_timestamp', 'address', 'amount']].reset_index()
transfers_all = transfers_all[['date', 'tx_timestamp', 'address', 'amount']]


#------------------------------------------------------------------------------------------------------------#

#------------------------------------------------------------------------------------------------------------#
#Create a df that has all the wallet addresses that have interacted with $MAGTC and the date of their first interaction

wallets_and_first_interaction = transfers_all.drop_duplicates(subset='address', keep='first')[['date', 'address']]
wallets_and_first_interaction['key']=1                                                   #Add a ['key'] column that can be used to join onto
wallets_and_first_interaction.columns = ['first_interaction_date', 'address', 'key']     #Rename the columns

#------------------------------------------------------------------------------------------------------------#
# Create a data_range df. You will join the wallet & first interactions onto the date range so we can create 
# a df with daily wallet balances that won't have interruptions
start_day=transfers_all['date'].min()
end_day=transfers_all['date'].max()

date_range = pd.DataFrame(pd.date_range(start_day, end_day, inclusive="both")).rename(columns={0:'date'}).reset_index()
date_range['key']=1

#------------------------------------------------------------------------------------------------------------#
# Merge the date range on wallet_list on the 'key' column created earlier. 
merged_wallets_date_range = date_range.merge(wallets_and_first_interaction, how='left', on='key')
merged_wallets_date_range['date'] = pd.to_datetime(merged_wallets_date_range['date']).dt.date

#Now merge all transfers onto the merged wallet_date_range df
merged_wallets_transfers=merged_wallets_date_range.merge(transfers_all, how='left', left_on =['date', 'address'], right_on=['date', 'address']).drop(['index_x', 'key', 'index_y'], axis=1)

#Create a mask to remove wallet data from the df on days that are earlier than the first wallet_interaction. This
# will help prevent having millions of rows of zeros before the wallets have even interacted
mask = merged_wallets_transfers['first_interaction_date']<=merged_wallets_transfers['date']
filtered_wallet_transfer_df=merged_wallets_transfers.loc[mask]
filtered_wallet_transfer_df.loc[:,'amount'].fillna(0)

#Group the transfers by date and sum up 'amount' columns to get the net daily change in MAGIC for a wallet
grouped_filtered_wallet_transfer=filtered_wallet_transfer_df.groupby(['date', 'address'])['amount'].sum().reset_index()

#Get a running total of transfers to get daily wallet balances
grouped_filtered_wallet_transfer['cumsum']=grouped_filtered_wallet_transfer.groupby(['address'])['amount'].cumsum()

#Now remove all rows for addresses that no longer have a balance and set the dataframe index to the date
wallet_balances=grouped_filtered_wallet_transfer[grouped_filtered_wallet_transfer['cumsum']>0].set_index('date')

#-----------------------------------------------------------------------------------------------------------------
#Save the wallet_balances to a .csv/.parquet file

wallet_balances.to_parquet(f'{date.today()}_balances_by_day.parquet')
wallet_balances.to_csv(f'{date.today()}_balances_by_day_{contract_address}.csv')

stop_time = time.time()
run_time = stop_time-start_time
print(f'the script took {run_time} seconds to run')

# print(latest_block)
# print(hex(int(latest_block.values)))

# pd.read_sql(sql_query, con=connection)