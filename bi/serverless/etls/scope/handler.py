from sqlalchemy import create_engine
import pandas as pd
import datetime
import numpy as np
from queries import Query
import sys
import environ
from pdb import set_trace as bp

env = environ.Env()
# reading .env file
environ.Env.read_env()

class ScopeETL(Query):
    def __init__(self, mode='daily'):
        
        super().__init__(mode)
        
        self.__mode = mode
        
        self.__action_if_table_exist = 'append'
        if self.__mode == 'historical':
            self.__action_if_table_exist = 'replace'
        
        CUATRO_UNO_URL = env('CUATRO_UNO_URL')
        DATALAKE_URL = env('DATALAKE_URL')
        
        self.__ORIGIN_CONN = create_engine(CUATRO_UNO_URL).connect()
        self.__DESTINY_CONN = create_engine(DATALAKE_URL).connect()
        
        self.__DF__COLUMN_NAMES = [
            'cellphone',
            'new_freemium_claim_at',
            'new_freemium_claim_parent_channel',
            'new_freemium_claim_partnership',
            'optin_template_id',
            'optin_at',
            'freeemium_at',
            'freemium_sku',
            'freemium_product'
        ]
        
        self.__ORDERED_DF_COLUMN_NAMES = [
            'cellphone',
            'new_freemium_claim_parent_channel',
            'new_freemium_claim_partnership',
            'new_freemium_claim_at',
            'optin_template_id',
            'optin_at',
            'freemium_sku',
            'freemium_product',
            'freeemium_at'
        ]
    
    def extract(self):
        
        yesterday_date = datetime.date.today() - datetime.timedelta(1)
        my_time = datetime.datetime.min.time()
        yesterday_datetime = datetime.datetime.combine(yesterday_date, my_time)
        yesterday_string = yesterday_datetime.strftime("%Y/%m/%d %H:%M:%S")
        
        new_freemium_claim_df = pd.read_sql(con=self.__ORIGIN_CONN,
                                            sql=self.NEW_FREEMIUM_CLAIM_QUERY,
                                            params={'yesterday': yesterday_string})
        
        optin_df = pd.read_sql(con=self.__ORIGIN_CONN,
                               sql=self.OPT_IN_QUERY,
                               params={'yesterday': yesterday_string})
        
        freemium_df = pd.read_sql(con=self.__ORIGIN_CONN,
                                  sql=self.FREEMIUM_QUERY,
                                  params={'yesterday': yesterday_string})
        
        self.__raw_array = [new_freemium_claim_df, optin_df, freemium_df]

    def transform(self):
        new_freemium_claim_df = self.__raw_array[0]
        optin_df = self.__raw_array[1]
        freemium_df = self.__raw_array[2]
        first_freemium_arrive_date = new_freemium_claim_df['first_freemium_arrive_date']
        
        new_freemium_claim_df['first_freemium_arrive_date'] = pd.to_datetime(first_freemium_arrive_date).dt.date
        optin_df['opt_in_date'] = pd.to_datetime(optin_df['opt_in_date']).dt.date
        freemium_df['purchased_at'] = pd.to_datetime(freemium_df['purchased_at']).dt.date
        
        new_freemium_claim_df.drop_duplicates(
            subset=[
                'cellphone',
                'first_freemium_arrive_date'],
            inplace=True)
        optin_df.drop_duplicates(subset=['cellphone','template_id'], inplace=True)
        freemium_df.drop_duplicates(subset=['cellphone','sku'], inplace=True)
        
        self.__transformed_df = pd.merge(new_freemium_claim_df, optin_df, on='cellphone', how='outer')
        self.__transformed_df = pd.merge(self.__transformed_df, freemium_df, on='cellphone', how='outer')
        
        self.__transformed_df.columns = self.__DF__COLUMN_NAMES
        self.__transformed_df = self.__transformed_df[self.__ORDERED_DF_COLUMN_NAMES]
        
        self.__transformed_df.replace(['null',None], np.nan, inplace=True)
        
        self.__transformed_df['new_freemium_claim_at'] = pd.to_datetime(self.__transformed_df['new_freemium_claim_at']).dt.date

    def load(self):        
        self.__transformed_df.to_sql(name='marketing_scorecard',
                                     con=self.__DESTINY_CONN,
                                     if_exists=self.__action_if_table_exist,
                                     index=False)

# Handler made as aws lambda handler
def lambda_handler(event, context):
    
    mode = 'daily'
    
    if len(sys.argv) > 1 and (sys.argv[1] == 'historical' or sys.argv[1] == 'hist'):
        mode = 'historical'
    
    print(mode)
    etl = ScopeETL(mode=mode)
    etl.extract()
    etl.transform()
    etl.load()

if __name__ == "__main__":
    lambda_handler(event={},context={})