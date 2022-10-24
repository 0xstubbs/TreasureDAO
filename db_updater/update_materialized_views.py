import os
from dotenv import load_dotenv
import psycopg2
import sqlalchemy
import time

load_dotenv()

def get_engine(user, passwd, host, port, db):
    url = f"postgresql://{user}:{passwd}@{host}:{port}/{db}"
    engine = sqlalchemy.create_engine(url, echo=False)
    
    return engine

def get_engine_from_settings():
    env_variables = dict(os.environ)
    keys = ['PG_DB_USERNAME', 'PG_DB_PASSWD', 'PG_DB_HOST', 'PG_DB_PORT', 'PG_DB_NAME']
    if not all(keys for key in keys if key in env_variables.keys()):
        raise Exception('Missing environment variable')
        
    return get_engine(env_variables['PG_DB_USERNAME'],
                      env_variables['PG_DB_PASSWD'],
                      env_variables['PG_DB_HOST'],
                      env_variables['PG_DB_PORT'],
                      env_variables['PG_DB_NAME']
                     )
def get_session():
    engine = get_engine_from_settings()
    session = sqlalchemy.sessionmaker(bind=engine)()
    return session

def get_pg2_connection():
    env_variables = dict(os.environ)
    keys = ['PG_DB_USERNAME', 'PG_DB_PASSWD', 'PG_DB_HOST', 'PG_DB_PORT', 'PG_DB_NAME']
    if not all(keys for key in keys if key in env_variables.keys()):
        raise Exception('Missing environment variable')
    try:
        conn = psycopg2.connect(
            dbname=env_variables['PG_DB_NAME'], 
            user=env_variables['PG_DB_USERNAME'], 
            port=env_variables['PG_DB_PORT'],
            host=env_variables['PG_DB_HOST'], 
            password=env_variables['PG_DB_PASSWD']
        )
    except psycopg2.DatabaseError as e:
        print(e)

    return conn
def update_all_materialized_views():
    start=time.time()
    print(
        """
        *********************************************************\n\n\
                Starting update of all materialized views\n\n\
        *********************************************************
        """
        )
    try:
        conn = get_pg2_connection()
        with conn.cursor() as cur:
            # cur.execute(
            #     """
            #     REFRESH MATERIALIZED VIEW bridgeworld_daily_balances;
            #     REFRESH MATERIALIZED VIEW bridgeworld_daily_erc721_balances;
            #     REFRESH MATERIALIZED VIEW l2_marketplace_magic_in;
            #     """)
            cur.execute("REFRESH MATERIALIZED VIEW bridgeworld_daily_balances;")
            interval1 = time.time()
            print(f'Refresh of bridgeworld_daily_balances tooks {interval1 - start} seconds...')
            cur.execute("REFRESH MATERIALIZED VIEW bridgeworld_daily_erc721_balances;")
            interval2=time.time()
            print(f'Refresh of bridgeworld_erc721 took {interval2-interval1} seconds....')
            cur.execute("REFRESH MATERIALIZED VIEW l2_marketplace_magic_in;")
            interval3 = time.time()
            print(f'Refresh of l2_marketplace_magic_in took {interval3-interval2} seconds....')
            cur.close()
            
            print('Views Refreshed')
            end = time.time()
            print(
            f"""
            *********************************************************\n\n\
                    Total refresh took {end - start} seconds\n\n\
            *********************************************************
            """)
            # print(f'Total refresh took {end - start} seconds....')
    except:
        print('there was an error')

update_all_materialized_views()
# print('Starting refresh of materialized views...')
# try:
#     conn = get_pg2_connection()
#     with conn.cursor() as cur:
#         cur.execute("REFRESH MATERIALIZED VIEW bridgeworld_daily_balances;")
#         interval1 = time.time()
#         print(f'Refresh of bridgeworld_daily_balances tooks {interval1 - start} seconds...')
#         cur.execute("REFRESH MATERIALIZED VIEW bridgeworld_daily_erc721_balances;")
#         interval2=time.time()
#         print(f'Refresh of bridgeworld_erc721 took {interval2-interval1} seconds....')
#         cur.execute("REFRESH MATERIALIZED VIEW l2_marketplace_magic_in;")
#         interval3 = time.time()
#         print(f'Refresh of l2_marketplace_magic_in took {interval3-interval2} seconds....')
#         cur.close()
#         print('Views Refreshed')
# except:
#     print('there was an error')





# pd.read_sql(sql_query, engine)