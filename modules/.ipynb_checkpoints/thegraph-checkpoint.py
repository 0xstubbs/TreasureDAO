#TheGraph API Integration
import requests
import pandas as pd
import numpy as np
import streamlit as st

@st.cache
def get_collections(cartridge_type):
    url = "https://api.thegraph.com/subgraphs/name/treasureproject/marketplace"
    if cartridge_type == 'Core':
        query = """
            {
            collections(
                where: { 
                id_in: 
                [
                    "0xfe8c1ac365ba6780aec5a985d989b327c27670a1-0"
                    , "0xfe8c1ac365ba6780aec5a985d989b327c27670a1-1"
                    , "0xfe8c1ac365ba6780aec5a985d989b327c27670a1-2"
                    , "0xebba467ecb6b21239178033189ceae27ca12eadf"
                    , "0xf3d00a2559d84de7ac093443bcaada5f4ee4165c"
                    , "0xbfeba04384cecfaf0240b49163ed418f82e43d3a"
                    , "0xe83c0200e93cb1496054e387bddae590c07f0194"
                    , "0xf0a35ba261ece4fc12870e5b7b9e7790202ef9b5"
                    , "0x21e1969884d477afd2afd4ad668864a0eebd644c"
                    
                    , "0x6325439389e0797ab35752b4f43a14c004f22a9c"
                    , "0x17dacad7975960833f374622fad08b90ed67d1b5"
                    , "0xf6cc57c45ce730496b4d3df36b9a4e4c3a1b9754"
                    , "0xae0d0c4cc3335fd49402781e406adf3f02d41bca"
                    , "0xb16966dad2b5a5282b99846b23dcdf8c47b6132c"
                    , "0xdf32aed1eb841a174cb637eaa1707026319fb563"
                    , "0xd666d1cc3102cd03e07794a61e5f4333b4239f53"
                    , "0xc5295c6a183f29b7c962df076819d44e0076860e"
                ]
                } 
            ) {
                name
                id
                contract
            }
            }
        """
    elif cartridge_type == "Partner":
        query = """
        {
          collections(
            where: { 
            id_in: 
            [

            , "0xdc758b92c7311280aeeb48096a3bf4d1c1f936d4"
            , "0x3956c81a51feaed98d7a678d53f44b9166c8ed66"
            , "0xcf51e9622471fb2bf2d66226a878280eabd71778"

            , "0x0af85a5624d24e2c6e7af3c0a0b102a28e36cea3"
            , "0xc43104775bd9f6076808b5f8df6cbdbeac96d7de-1"
            , "0xc43104775bd9f6076808b5f8df6cbdbeac96d7de-2"

            , "0x4de95c1e202102e22e801590c51d7b979f167fbb"
            , "0x8762DbD391Fd90b29eccBB628CD54bD92F5Fc1f3"
            , "0x20251F0ee19917bDe625Ba9eBf79aD3b7769f673"
            , "0x8ec68F970e1c61b44B6d81c3b78Ca931C6FFc92d"
            , "0xCE3051ff2ED963406b55ef505751eF88B8f0D791"
            , "0x747910B74D2651A06563C3182838EAE4120F4277"
            , "0x09cae384c6626102abe47ff50588a1dbe8432174"
            , "0x5e0ba87362f239bDBF40E621Fa11DBD50d190389"
            ,"0x00000000016c35e3613ad3ed484aa48f161b67fd"
            ,"0x32A322C7C77840c383961B8aB503c9f45440c81f"
            ,"0xf7fbe8eec9063aa518d11639565b018468bb4abb"
            ,"0x6f2aa70c70625e45424652aed968e3971020f205"
            ,"0x9f0cc315cae0826005b94462b5400849b3d39d91"
            ,"0x37865fe8a9c839f330f35104eed08d4e8136c339"
            ,"0x7480224ec2b98f28cee3740c80940a2f489bf352"
            ,"0x381227255ef6c5d85966b78d13e4b4a4c8719b5e"
            ,"0x89A8Fe072c1193A1C4cfBe4f3787f5681BaBf9ae"
            ,"0x71bd1562f7e0f182f8be472151befdfb824e26be"
            ,"0x5e01c1889085b528eeff5e1bee64bfe94f454703"   
            ]
            } 
        ) {
            name
            id
            contract
        }
        } 
        """
    elif cartridge_type == "All":
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