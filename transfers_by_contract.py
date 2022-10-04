import pandas as pd
from dotenv import load_dotenv
import os
import numpy as np
import requests
import time
from datetime import date

def get_response_wo_pagekey(contract_address, ALCHEMY_API_KEY_TREASURE):
  url = f"https://arb-mainnet.g.alchemy.com/v2/{ALCHEMY_API_KEY_TREASURE}"
  payload = {
      "id": 1,
      "jsonrpc": "2.0",
      "method": "alchemy_getAssetTransfers",
      "params": [
          {
              "fromBlock": "0x0",
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

def get_response_w_pgkey(ALCHEMY_API_KEY_TREASURE, contract_address, _page_key):
    url = f"https://arb-mainnet.g.alchemy.com/v2/{ALCHEMY_API_KEY_TREASURE}"
  # contract_address = "0x539bdE0d7Dbd336b79148AA742883198BBF60342"
    payload = {
      "id": 1,
      "jsonrpc": "2.0",
      "method": "alchemy_getAssetTransfers",
      "params": [
          {
              "fromBlock": "0x0",
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
ALCHEMY_API_KEY_TREASURE = os.getenv('ALCHEMY_API_KEY_TREASURE')    

start_time = time.time()
# contract_address = "0x4de95c1e202102e22e801590c51d7b979f167fbb"

# contract_list = ["0x747910b74d2651a06563c3182838eae4120f4277", "0x4de95c1e202102e22e801590c51d7b979f167fbb","0x8ec68f970e1c61b44b6d81c3b78ca931c6ffc92d"
#                  , "0x8762dbd391fd90b29eccbb628cd54bd92f5fc1f3", "0xa56aa79eef0651a0d04b00da4f6263bcec841184", "0x20251f0ee19917bde625ba9ebf79ad3b7769f673"
#                  ,"0xce3051ff2ed963406b55ef505751ef88b8f0d791"]


# contract_list = ["0xf0a35ba261ece4fc12870e5b7b9e7790202ef9b5",'0x21e1969884d477afd2afd4ad668864a0eebd644c', '0xfe8c1ac365ba6780aec5a985d989b327c27670a1'
#                  , '0x658365026d06f00965b5bb570727100e821e6508','0xe83c0200e93cb1496054e387bddae590c07f0194', 
contract_list = ['0xf3d00a2559d84de7ac093443bcaada5f4ee4165c','0xebba467ecb6b21239178033189ceae27ca12eadf', '0xbfeba04384cecfaf0240b49163ed418f82e43d3a']


# contract_list = []
for contract in contract_list:
    print(f"Contract: {contract}")
    page_key = None
    concat_num=0
    skip_other_pages=False
    df_transfers = pd.DataFrame()

    response_0 = get_response_wo_pagekey(contract, ALCHEMY_API_KEY_TREASURE)
    print(response_0.keys())
    if 'pageKey' in response_0:
        page_key = response_0['pageKey']
    else:
        print('Not enough for second page')
        skip_other_pages = True
    df_transfers = pd.concat([df_transfers, pd.json_normalize(response_0['transfers'])], axis=0)

    while True:
        if not skip_other_pages:
            response=get_response_w_pgkey(ALCHEMY_API_KEY_TREASURE, contract, page_key)
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
    df_transfers.to_csv(f'{date.today()}_df_transfers_{contract}.csv')
    df_transfers.to_csv('df_transfers.csv')

    stop_time = time.time()
    run_time = stop_time-start_time
print(f'the script took {run_time} seconds to run')