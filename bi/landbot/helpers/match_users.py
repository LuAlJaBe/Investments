import pandas as pd
from landbot.helpers.queries import Query
from sqlalchemy import create_engine
import environ
from os.path import join, dirname

env = environ.Env()
# reading .env file
environ.Env.read_env(join(dirname(dirname(dirname(__file__))),'bi','.env'))

class ZendeskExcelFile(Query):
    def __init__(self, name):
        super().__init__()
        self.__file_extension = name.split('.')[1]
        self.__path = join(dirname(dirname(dirname(dirname(__file__)))), 'vol', 'web', 'media', 'uploads', name)
        self.DB_USER = env('DB_USER')
        self.DB_PASSWORD = env('DB_PASSWORD')
        self.DB_NAME = env('DB_NAME')
        self.DB_HOST = env('DB_HOST')
        self.DB_PORT = env('DB_PORT')
        
    def set_excel_df(self):
        if self.__file_extension == 'xlsx':
            self.excel_df = pd.read_excel(self.__path, engine='openpyxl')
        elif self.__file_extension == 'xls':
            self.excel_df = pd.read_excel(self.__path)
        elif self.__file_extension == 'csv':
            self.excel_df = pd.read_csv(self.__path)
        
    def set_zendesk_ids(self):
        zendesk_values = self.excel_df['ID del solicitante'].values
        self.zendesk_ids = tuple(zendesk_values)
    
    def set_c4uno_conn(self):
        c4uno_read_replica_url = 'mysql+pymysql://'+self.DB_USER+':'+self.DB_PASSWORD+'@'+self.DB_HOST+':'+self.DB_PORT+'/'+self.DB_NAME+'?charset=utf8mb4'
        self.c4uno_conn = create_engine(c4uno_read_replica_url).connect()
        
    def set_query_df(self):
        self.query_df = pd.read_sql(con=self.c4uno_conn, sql=self.users_companies_match_query, params={'zendesk_ids':self.zendesk_ids})
        self.query_df.drop_duplicates(subset=['user_id'],keep='last',inplace=True)
    
    def merge_excel_and_query_dataframes(self):
        self.query_df[['service_user_id']] = self.query_df[['service_user_id']].apply(pd.to_numeric)
        self.new_excel_df = self.excel_df.merge(self.query_df, left_on='ID del solicitante', right_on='service_user_id', how='left')
    
    def save_excel(self):
        # Export as xlsx
        self.__writer = pd.ExcelWriter(self.__path)
        self.new_excel_df.to_excel(self.__writer, 'Nueva consulta ANDREA', index=False)
        self.__writer.save()
    
    def match(self):
        self.set_excel_df()
        self.set_zendesk_ids()
        self.set_c4uno_conn()
        self.set_query_df()
        self.merge_excel_and_query_dataframes()
        self.save_excel()