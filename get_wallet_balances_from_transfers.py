import pandas as pd
import numpy as np
from datetime import date

#------------------------------------------------------------------------------#
#--------------------Get Unique Wallets------------------------------------
# # unique_wallets = pd.DataFrame(_transformed_transfers['address'].unique())
# print('Getting all unique addresses...')
# wallets = df_transfers['address'].drop_duplicates()
# wallets['key']=1

# ##-------------
# #-----Create a date range dataframe

# start_day = pd.to_datetime(df_transfers['tx_timestamp'].dt.date).min()
# end_day = pd.to_datetime(df_transfers['tx_timestamp'].dt.date).max()
# date_range = pd.DataFrame(pd.date_range(start_day, end_day, inclusive="both"))
# date_range['key']=1

# wallets_all_days=pd.merge(unique_wallets, date_range, how='outer', on='key').drop(columns=['key']).rename(columns={'0_x':'wallet_address', '0_y':'date'})




# print(df_all_wallets_all_days_n_changes.head())
# print(df_all_wallets_all_days_n_changes.info())

# unique_holders_per_day = get_unique_holders_per_day(df_all_wallets_all_days_n_changes)
# print(unique_holders_per_day.head())
# print(unique_holders_per_day.info())

# wallet_balance_n_changes = get_wallet_bal_net_change(df_all_wallets_all_days_n_changes)
# print(wallet_balance_n_changes.head())
# print(wallet_balance_n_changes.info())

# df_mints_n_burns = mints_n_burns(df_transfers, 'df')
# total_supply = mints_n_burns(df_transfers, 'total_supply')

# df_mints_n_burns.to_csv(f'{date.today()}_magic_supply_over_time.csv')
# wallet_balance_n_changes.to_csv(f'{date.today()}_wallet_balances.csv')


#------------------------------------------------------------------------------------------------------------#
#
#                                          Read the data from CSV Files
#
#------------------------------------------------------------------------------------------------------------#

#Read in the csv/parquet file that has the raw transaction data
df_transfers = pd.read_csv('/home/stubbs/Documents/skycatcher/TreasureDAO/df_transfers.csv' 
                          , usecols=['hash', 'from', 'to', 'value', 'rawContract.address', 'metadata.blockTimestamp']
                            , parse_dates=['metadata.blockTimestamp']
                          )

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
transfers_all = transfers_all[['date', 'tx_timestamp', 'address', 'amount']].reset_index()

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
wallet_balances.to_csv(f'{date.today()}_balances_by_day.csv')
#-----------------------------------------------------------------------------------------------------------------#
#-----------------------------------------------------------------------------------------------------------------#
#-----------------------------------------------------------------------------------------------------------------#
#----------------------------------Upload parquet file to Amazon S3 Bucket----------------------------------------#
import boto3
import os
from dotenv import load_dotenv

def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True

#Get Amazon S3 credentials from .env
load_dotenv()
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')         #Access key should start w/ 'AKIA'. If creds are downloaded from S3 it will be in the 'Password' column
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY') #Secret access key should start w/ 'UEVCA'. Downloaded creds have it in the 'Access key ID' column.

s3 = boto3.client('s3',
                   region_name='us-west-1',
                   aws_access_key_id=AWS_ACCESS_KEY_ID,
                   aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

bucket_name = "stubbs-file-storage-streamlit"
object_name = "balances_by_day.parquet"

# s3=boto3.client('s3')
with open('./2022-09-12_balances_by_day.parquet', "rb") as f:
    s3.upload_fileobj(f, bucket_name, object_name)
    
#----------------------------------------------------------------------------------------------------------------------#