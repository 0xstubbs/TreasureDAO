from gettext import npgettext
import pandas as pd
import numpy as np
import requests

def get_CollectionFromMarketplace():
    url = "https://api.thegraph.com/subgraphs/name/vinnytreasure/treasuremarketplace-fast-prod"

    query = """
    {
    marketplaces{
        collections{
        id
        fee{
            collectionFee
        }
        currency{
            id
        }
        stat{
            sales
            volume
        }
        }
    }
    }
    """

    print(query)
    response = requests.post(url, json={'query':query})
    print(response.status_code)

    marketplace = pd.json_normalize(response.json()['data']['marketplaces'],
                    record_path =['collections']).drop(columns=('fee'))
    
    return marketplace


import asyncio
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
import pandas as pd


async def get_collections():
    subgraph_url = "https://api.thegraph.com/subgraphs/name/vinnytreasure/treasuremarketplace-fast-prod"

    transport = AIOHTTPTransport(
        url=subgraph_url
        )
    client = Client(transport=transport, fetch_schema_from_transport=True)


    query = gql ("""
    {
    collections{
      id
      fee{
        collectionFee
      }
      stat{
        id
        sales
        volume
      }
    }
    }
    """)

    # params = {"collectionId": collectionId, "tokenId":tokenId}
    # reponse = await client.execute_async(query, params)
    response = await client.execute_async(query)


    collections = pd.json_normalize(response,
                      record_path =['collections']).drop(['fee'], axis=1)

    print(collections)
    return collections

# print('Running get_collections()...')
# collections = asyncio.run(get_collections())
# print('\n\nFinished running get_collections()..')
# collections.head()
# print(f'collections.info()....\n{collections.info()}')

from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
import numpy as np
import pandas as pd

def get_collections():
    ### Get the collections listed in Trove Marketplace
    ### The returned dataframe has the following:
    ### collection_id: the collection id (which is all lowercase contract address)
    ### collection_fee: the fee for sales on the trove marketplace
    ### total_num_sales: # of collection sales
    ### total_volume_sales: Total volume of collection sales
    
    url = "https://api.thegraph.com/subgraphs/name/vinnytreasure/treasuremarketplace-fast-prod"
    transport = RequestsHTTPTransport(
        url=url,
        verify=True,
        retries=3,
    )
    client = Client(transport=transport, 
                    fetch_schema_from_transport=True)
    
    last_id = ""

    df=pd.DataFrame()
    while True:
        
        query = gql ("""
        query collectionBatches($lastId: ID){
        collections(first:100, where:{id_gt:$lastId}){
          id
          fee{
            collectionFee
          }
          stat{
            sales
            volume
          }
        }
        }
        """)
        params = {'lastId': last_id}
        result = client.execute(query, params)
        # print(result)
        
        ### Check if the result has any items in the 'collections' list. if the list is empty then we have no more results remaining
        if len(result['collections']) == 0:
            print(f'the last_id is <>{last_id}</> and the the loop is done')
            break
        else: 
            collections = pd.json_normalize(result, record_path =['collections'])
            last_id = np.array(collections['id'].values)[-1]
            df = pd.concat([df, collections], axis=0)
            
    df = df.drop('fee', axis = 1)
    df = df.rename(columns={'id': 'collection_id', 'fee.collectionFee': 'collection_fee', 'stat.sales': 'total_num_sales', 'stat.volume':'total_volume_sales'})
    return df
