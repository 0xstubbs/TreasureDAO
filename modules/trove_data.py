import requests
import pandas as pd
import numpy as np

import asyncio
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.requests import RequestsHTTPTransport

def get_current_listings(collectionList: list )-> list:
    
    # transport = AIOHTTPTransport(url="https://api.thegraph.com/subgraphs/name/vinnytreasure/treasuremarketplace-fast-prod")
    transport = RequestsHTTPTransport(
        url="https://api.thegraph.com/subgraphs/name/vinnytreasure/treasuremarketplace-fast-prod",
        verify=True,
        retries=5
    )
    client = Client(transport=transport, fetch_schema_from_transport=True)

    df = pd.DataFrame()
    last_block_number = 0

    for selectedCollection in collectionList:
        while True:
            
            query = gql(
            """
            query($lastBlockNumber: BigInt!, $selectedCollection: ID!){
            collections(first:100, where: {id: $id_list}){
                id
                listings(where: {blockNumber_gt: $lastBlockNumber}){
                    token{
                        id
                        tokenId
                        }
                    status
                    blockNumber
                    timestamp
                    pricePerItem
                    }
                }
            }
            """
            )
            
            params = {"lastBlockNumber": last_block_number, 'selectedCollection': selectedCollection}
            result= client.execute(query, params)
            # result = await client.execute_async(query, params)
            
            if 'error' in result:
                break
            try:
                df_new = pd.json_normalize(result,
                            record_path=['collections', 'listings'],
                            meta=[['collections', 'id']],
                            meta_prefix='--',
                            errors='ignore'
                            ).sort_values('blockNumber', ascending=True)
                last_block_number = df_new['blockNumber'].max()
                print(f"lastBlockNumber: {last_block_number}")
                df=pd.concat([df, df_new], axis=0)
            except:
                print(result['collections'])
                break
            
        df=df.astype({'pricePerItem': float, 'blockNumber':float, 'token.tokenId':int})
        df['pricePerItem']=df.loc[:,'pricePerItem']/pow(10,18)
        return df[df['status']=='ACTIVE'].drop_duplicates().sort_values('pricePerItem', ascending=True)



def get_sales_and_listings():
    transport = RequestsHTTPTransport(
        url="https://api.thegraph.com/subgraphs/name/vinnytreasure/treasuremarketplace-fast-prod",
        verify=True,
        retries=5
        )
    client = Client(transport=transport, fetch_schema_from_transport=True)

    df = pd.DataFrame()
    last_block_number = 0

    while True:
        
        query = gql(
        """
        query($lastBlockNumber: BigInt!){
        sales(first:100, where: {block_gt:$lastBlockNumber})
        {
            block
            timestamp
            pricePerItem
            type
            currency{
                id
                volume
            }
            token{
                id
                collection{
                    id
                }
                tokenId
                stat{
                    sales
                    volume
                }
            }
        }}
        """
        )
        
        params = {"lastBlockNumber": last_block_number}
        result= client.execute(query, params)
        
        df_new=pd.json_normalize(result,
                             record_path=['sales'],
                             errors='ignore')
        df=pd.concat([df,df_new], axis=0)




response=get_current_listings()
print(response)

    