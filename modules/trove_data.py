import requests
import pandas as pd
import numpy as np

import asyncio
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.requests import RequestsHTTPTransport

# def get_current_listings(collectionList: list )-> list:
    
#     # transport = AIOHTTPTransport(url="https://api.thegraph.com/subgraphs/name/vinnytreasure/treasuremarketplace-fast-prod")
#     transport = RequestsHTTPTransport(
#         url="https://api.thegraph.com/subgraphs/name/vinnytreasure/treasuremarketplace-fast-prod",
#         verify=True,
#         retries=5
#     )
#     client = Client(transport=transport, fetch_schema_from_transport=True)

#     df = pd.DataFrame()
#     last_block_number = 0

#     for selectedCollection in collectionList:
#         while True:
            
#             query = gql(
#             """
#             query($lastBlockNumber: BigInt!, $selectedCollection: ID!){
#             collections(first:100, where: {id: $id_list}){
#                 id
#                 listings(where: {blockNumber_gt: $lastBlockNumber}){
#                     token{
#                         id
#                         tokenId
#                         }
#                     status
#                     blockNumber
#                     timestamp
#                     pricePerItem
#                     }
#                 }
#             }
#             """
#             )
            
#             params = {"lastBlockNumber": last_block_number, 'selectedCollection': selectedCollection}
#             result= client.execute(query, params)
#             # result = await client.execute_async(query, params)
            
#             if 'error' in result:
#                 break
#             try:
#                 df_new = pd.json_normalize(result,
#                             record_path=['collections', 'listings'],
#                             meta=[['collections', 'id']],
#                             meta_prefix='--',
#                             errors='ignore'
#                             ).sort_values('blockNumber', ascending=True)
#                 last_block_number = df_new['blockNumber'].max()
#                 print(f"lastBlockNumber: {last_block_number}")
#                 df=pd.concat([df, df_new], axis=0)
#             except:
#                 print(result['collections'])
#                 break
            
#         df=df.astype({'pricePerItem': float, 'blockNumber':float, 'token.tokenId':int})
#         df['pricePerItem']=df.loc[:,'pricePerItem']/pow(10,18)
#         return df[df['status']=='ACTIVE'].drop_duplicates().sort_values('pricePerItem', ascending=True)



# def get_sales_and_listings():
#     transport = RequestsHTTPTransport(
#         url="https://api.thegraph.com/subgraphs/name/vinnytreasure/treasuremarketplace-fast-prod",
#         verify=True,
#         retries=5
#         )
#     client = Client(transport=transport, fetch_schema_from_transport=True)

#     df = pd.DataFrame()
#     last_block_number = 0

#     while True:
        
#         query = gql(
#         """
#         query($lastBlockNumber: BigInt!){
#         sales(first:100, where: {block_gt:$lastBlockNumber, collection:$})
#         {
#             block
#             timestamp
#             pricePerItem
#             type
#             currency{
#                 id
#                 volume
#             }
#             token{
#                 id
#                 collection{
#                     id
#                 }
#                 tokenId
#                 stat{
#                     sales
#                     volume
#                 }
#             }
#         }}
#         """
#         )
#         params = {"lastBlockNumber": last_block_number}
#         result= client.execute(query, params)
        
#         df_new=pd.json_normalize(result,
#                              record_path=['sales'],
#                              errors='ignore')
#         df=pd.concat([df,df_new], axis=0)




# # response=get_current_listings()
# # print(response)

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

def get_collection_info():
    url = "https://api.thegraph.com/subgraphs/name/treasureproject/marketplace"
    query = """
            {
    collections{
        name
        id
        contract
        }
        }
    """
    response = requests.post(url, json={'query':query}).json()['data']['collections']
    collections = pd.json_normalize(response)
    return collections


    