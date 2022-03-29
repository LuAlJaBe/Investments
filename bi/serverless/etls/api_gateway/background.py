from boto3 import client
from datetime import date, datetime, timedelta
import environ
import sys
from botocore.config import Config
from os.path import join, dirname

# Load environment variables in AWS Lambda
#import os
#APIGATEWAY_PRODUCTION_LOG_GROUP = os.environ('APIGATEWAY_PRODUCTION_LOG_GROUP')
#APIGATEWAY_PRODUCTION_S3 = os.environ('APIGATEWAY_PRODUCTION_S3')
#APIGATEWAY_SANDBOX_LOG_GROUP = os.environ('APIGATEWAY_SANDBOX_LOG_GROUP')
#APIGATEWAY_SANDBOX_S3 = os.environ('APIGATEWAY_SANDBOX_S3')
#AWS_ACCESS_KEY = os.environ('AWS_ACCESS_KEY')
#AWS_SECRET_KEY = os.environ('AWS_SECRET_KEY')

env = environ.Env()
# reading .env file
environ.Env.read_env(join(dirname(dirname(dirname(dirname(__file__)))),'bi','.env'))

class Background():
    def __init__(self, mode='daily'):
        self.__config = Config(
            region_name = 'us-west-2',
            signature_version = 'v4',
            retries = {
                'max_attempts': 10,
                'mode': 'standard'
            }
        )
        self.__yesterday = date.today()- timedelta(days=1)
        self.__yesterday_str = self.__yesterday.__str__()
        self.__from_timestamp = int(datetime.strptime(self.__yesterday_str, "%Y-%m-%d").timestamp() * 1000)
        self.__to_timestamp = self.__from_timestamp + 86400000
        if mode == 'historical':
            self.__from_timestamp = 1635724800000 # 2021/11/01 00:00:00 in miliseconds
            self.__to_timestamp = int(datetime.strptime(self.__yesterday_str, "%Y-%m-%d").timestamp() * 1000)

        APIGATEWAY_PRODUCTION_LOG_GROUP = env('APIGATEWAY_PRODUCTION_LOG_GROUP')
        APIGATEWAY_PRODUCTION_S3 = env('APIGATEWAY_PRODUCTION_S3')
        APIGATEWAY_SANDBOX_LOG_GROUP = env('APIGATEWAY_SANDBOX_LOG_GROUP')
        APIGATEWAY_SANDBOX_S3 = env('APIGATEWAY_SANDBOX_S3')
        AWS_ACCESS_KEY = env('AWS_ACCESS_KEY')
        AWS_SECRET_KEY = env('AWS_SECRET_KEY')
        
        self.__prod_log_group_name = APIGATEWAY_PRODUCTION_LOG_GROUP
        self.__prod_destination = APIGATEWAY_PRODUCTION_S3
        self.__prod_logs_client = client('logs',
                                    config=self.__config,
                                    aws_access_key_id=AWS_ACCESS_KEY,
                                    aws_secret_access_key=AWS_SECRET_KEY,)
        self.__sandbox_log_group_name = APIGATEWAY_SANDBOX_LOG_GROUP
        self.__sandbox_destination = APIGATEWAY_SANDBOX_S3
        self.__sandbox_logs_client = client('logs',
                                    config=self.__config,
                                    aws_access_key_id=AWS_ACCESS_KEY,
                                    aws_secret_access_key=AWS_SECRET_KEY,)
        
    def load(self):
        response = self.__prod_logs_client.create_export_task(
            logGroupName=self.__prod_log_group_name,
            fromTime=self.__from_timestamp,
            to=self.__to_timestamp,
            destination=self.__prod_destination
        )
        print(response)
        response = self.__sandbox_logs_client.create_export_task(
            logGroupName=self.__sandbox_log_group_name,
            fromTime=self.__from_timestamp,
            to=self.__to_timestamp,
            destination=self.__sandbox_destination
        )
        print(response)

def lambda_handler(event, context):
    
    mode = 'daily'
    
    if len(sys.argv) > 1 and (sys.argv[1] == 'historical' or sys.argv[1] == 'hist'):
        mode = 'historical'
    
    print('API Gateway Background Mode', mode)
    background = Background(mode=mode)
    background.load()

if __name__ == "__main__":
    lambda_handler(event={},context={})