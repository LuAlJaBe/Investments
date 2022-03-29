from sqlalchemy import create_engine
import pandas as pd
import numpy as np
import os
import glob
import boto3
import gzip
import re
import json
import environ
from os.path import join, dirname
import shutil
from pdb import set_trace as bp

# Load environment variables in AWS Lambda
#DB_USER_DATALAKE = os.environ('DB_USER_DATALAKE')
#DB_PASSWORD_DATALAKE = os.environ('DB_PASSWORD_DATALAKE')
#DB_NAME_DATALAKE = os.environ('DB_NAME_DATALAKE')
#DB_HOST_DATALAKE = os.environ('DB_HOST_DATALAKE')
#DB_PORT_DATALAKE = os.environ('DB_PORT_DATALAKE')

env = environ.Env()
# reading .env file
environ.Env.read_env(join(dirname(dirname(dirname(dirname(__file__)))),'bi','.env'))

DB_USER_DATALAKE = env('DB_USER_DATALAKE')
DB_PASSWORD_DATALAKE = env('DB_PASSWORD_DATALAKE')
DB_NAME_DATALAKE = env('DB_NAME_DATALAKE')
DB_HOST_DATALAKE = env('DB_HOST_DATALAKE')
DB_PORT_DATALAKE = env('DB_PORT_DATALAKE')
AWS_ACCESS_KEY = env('AWS_ACCESS_KEY')
AWS_SECRET_KEY = env('AWS_SECRET_KEY')

class APIGateway():
    def __init__(self):
        self.datalake_url = 'mysql+pymysql://'+DB_USER_DATALAKE+':'+DB_PASSWORD_DATALAKE+'@'+DB_HOST_DATALAKE+':'+DB_PORT_DATALAKE+'/'+DB_NAME_DATALAKE+'?charset=utf8mb4'
        self.datalake_conn = create_engine(self.datalake_url).connect()

        self.s3_resource = boto3.resource('s3',
                                    aws_access_key_id=AWS_ACCESS_KEY,
                                    aws_secret_access_key= AWS_SECRET_KEY)
        self.s3_client = boto3.client('s3',
                                aws_access_key_id=AWS_ACCESS_KEY,
                                aws_secret_access_key= AWS_SECRET_KEY)

        try:
            os.mkdir('production_exportedlogs')
        except:
            pass

        self.bucket = self.s3_resource.Bucket('bamba-api-gateway-logs-prod')
        print(self.bucket)

        iterator = 0
        for s3_object in self.bucket.objects.all():
            file_name = 'production_exportedlogs/' + str(iterator)
            print(file_name)
            with open(file_name, 'wb') as f:
                self.s3_client.download_fileobj(self.bucket.name, s3_object.key, f)
            iterator += 1

        self.request_data_dictionary = {}

    def eri(self, args):
        string_date, request_reference, main_string = args
        request_id = main_string.split(':')[1].replace(" ", "")
        self.request_data_dictionary[request_reference] = {
            "request_id": request_id,
            "request_reference": request_reference,
            "request_start_at": string_date
        }

    def vupor(self, args):
        string_date, request_reference, main_string = args
        match_string = "Verifying Usage Plan for request: " + request_reference + ". API Key: "
        main_string = main_string.replace(match_string, "")
        verifying_array = main_string.split("API Stage:")
        api_key = verifying_array[0].replace(" ", "")
        api_stage = verifying_array[1].replace(" ", "")
        self.request_data_dictionary[request_reference]["verify_init_at"] = string_date
        self.request_data_dictionary[request_reference]["api_key"] = api_key
        self.request_data_dictionary[request_reference]["api_stage"] = api_stage

    def akna(self, args):
        string_date, request_reference, main_string = args
        self.request_data_dictionary[request_reference]["verify_result"] = main_string
        self.request_data_dictionary[request_reference]["verify_result_at"] = string_date

    def upcsfak(self, args):
        string_date, request_reference, main_string = args
        self.request_data_dictionary[request_reference]["verify_result"] = main_string
        self.request_data_dictionary[request_reference]["verify_result_at"] = string_date

    def sefr(self, args):
        string_date, request_reference, main_string = args
        self.request_data_dictionary[request_reference]["start_request_at"] = string_date

    def httpm(self, args):
        string_date, request_reference, main_string = args
        main_string = main_string.replace("HTTP Method:", "")
        http_array = main_string.split(", Resource Path:")
        http_method = http_array[0].replace(" ", "")
        resource_path = http_array[1].replace(" ", "")
        self.request_data_dictionary[request_reference]["http_method"] = http_method
        self.request_data_dictionary[request_reference]["resource_path"] = resource_path

    def ak(self, args):
        string_date, request_reference, main_string = args
        api_key = main_string.replace("API Key: ", "")
        if "api_key" not in self.request_data_dictionary[request_reference]:
            self.request_data_dictionary[request_reference]['api_key'] = api_key
        elif api_key == self.request_data_dictionary[request_reference]["api_key"]:
            #print("[API Key Verified]")
            pass
        else:
            #print("::::::::::::::::::::::::::::::::::::Warning::::::::::::::::::::::::::::::::::::")
            pass

    def aki(self, args):
        string_date, request_reference, main_string = args
        api_key_id = main_string.replace("API Key ID:", "")
        self.request_data_dictionary[request_reference]["api_key_id"] = api_key_id.replace(" ","")

    def mrp(self, args):
        string_date, request_reference, main_string = args
        method_request_path = main_string.replace("Method request path: ", "")
        self.request_data_dictionary[request_reference]["method_request_path"] = method_request_path.replace(" ","")

    def mrqs(self, args):
        string_date, request_reference, main_string = args
        method_request_query_string = main_string.replace("Method request query string: ", "")
        self.request_data_dictionary[request_reference]["method_request_query_string"] = method_request_query_string.replace(" ","")

    def mreqh(self, args):
        string_date, request_reference, main_string = args
        method_request_headers = main_string.replace("Method request headers:", "")
        self.request_data_dictionary[request_reference]["method_request_headers"] = method_request_headers.replace(" ","")

    def mrbbt(self, args):
        string_date, request_reference, main_string = args
        method_request_body_before_transformations = main_string.replace("Method request body before transformations:", "")
        self.request_data_dictionary[request_reference]["method_request_body_before_transformations"] = method_request_body_before_transformations.replace(" ","")

    def eru(self, args): 
        string_date, request_reference, main_string = args
        endpoint_request_uri = main_string.replace("Endpoint request URI:", "")
        self.request_data_dictionary[request_reference]["endpoint_request_uri"] = endpoint_request_uri.replace(" ","")

    def ereqh(self, args):
        string_date, request_reference, main_string = args
        endpoint_request_headers = main_string.replace("Endpoint request headers:", "")
        self.request_data_dictionary[request_reference]["endpoint_request_headers"] = endpoint_request_headers.replace(" ","")

    def erbat(self, args):
        string_date, request_reference, main_string = args
        endpoint_request_body_after_transformation = main_string.replace("Endpoint request body after transformations:", "")
        self.request_data_dictionary[request_reference]["endpoint_request_body_after_transformation"] = endpoint_request_body_after_transformation.replace(" ","")

    def sr(self, args):
        string_date, request_reference, main_string = args
        self.request_data_dictionary[request_reference]["send_request_at"] = string_date

    def rr(self, args):
        string_date, request_reference, main_string = args
        main_string = main_string.replace("Received response. Status:", "")
        received_response_array = main_string.split(", Integration latency:")
        response_status = received_response_array[0].replace(" ", "")
        response_latency = received_response_array[1].replace(" ", "")
        self.request_data_dictionary[request_reference]["response_status"] = response_status
        self.request_data_dictionary[request_reference]["response_latency"] = response_latency
        self.request_data_dictionary[request_reference]["response_received_at"] = string_date

    def eresh(self, args):
        string_date, request_reference, main_string = args
        endpoint_response_headers = main_string.replace("Endpoint response headers:", "")
        self.request_data_dictionary[request_reference]["endpoint_response_headers"] = endpoint_response_headers.replace(" ","")

    def erbbt(self, args):
        string_date, request_reference, main_string = args
        endpoint_response_body_before_transformations = main_string.replace("Endpoint response body before transformations:", "")
        self.request_data_dictionary[request_reference]["endpoint_response_body_before_transformations"] = endpoint_response_body_before_transformations.replace(" ","")

    def mrbat(self, args):
        string_date, request_reference, main_string = args
        method_response_body_after_transformations = main_string.replace("Method response body after transformations:", "")
        self.request_data_dictionary[request_reference]["method_response_body_after_transformations"] = method_response_body_after_transformations.replace(" ","")

    def mresh(self, args):
        string_date, request_reference, main_string = args
        method_response_headers = main_string.replace("Method response headers:", "")
        self.request_data_dictionary[request_reference]["method_response_headers"] = method_response_headers.replace(" ","")

    def sce(self, args):
        string_date, request_reference, main_string = args
        self.request_data_dictionary[request_reference]["successfully_completed_at"] = string_date
        #print(self.request_data_dictionary[request_reference])

    def mcws(self, args):
        string_date, request_reference, main_string = args
        response_status = main_string.replace("Method completed with status: ", "")
        if "response_status" not in self.request_data_dictionary[request_reference]:
            self.request_data_dictionary[request_reference]["response_status"] = response_status    
        elif response_status == self.request_data_dictionary[request_reference]["response_status"]:
            #print("[response_status Verified]")
            pass
        else:
            #print("::::::::::::::::::::::::::::::::::::Warning::::::::::::::::::::::::::::::::::::")
            pass

    def event_processor(self, args):
        string_date, request_reference, main_string = args
        event = main_string.split(':')[0]
        if re.match("^Extended Request Id$",event):
            varible_info = self.eri(args)
            #print("ERI")
        elif re.match("^Verifying Usage Plan for request$",event):
            varible_info = self.vupor(args)
            #print("VUPOR")
        elif re.match("^API Key.*not authorized",event):
            varible_info = self.akna(args)
            #print("AKNA")
        elif re.match("^Usage Plan check succeeded for API Key",event):
            varible_info = self.upcsfak(args)
            #print("UPCSFAK")
        elif re.match("^Starting execution for request$",event):
            varible_info = self.sefr(args)
            #print("SEFR")
        elif re.match("^HTTP Method$",event):
            varible_info = self.httpm(args)
            #print("HTTPM")
        elif re.match("^API Key$",event):
            varible_info = self.ak(args)
            #print("AK")
        elif re.match("^API Key ID$",event):
            varible_info = self.aki(args)
            #print("AKI")
        elif re.match("^Method request path$",event):
            varible_info = self.mrp(args)
            #print("MRP")
        elif re.match("^Method request query string$",event):
            varible_info = self.mrqs(args)
            #print("MRQS")
        elif re.match("^Method request headers$",event):
            varible_info = self.mreqh(args)
            #print("MREQH")
        elif re.match("^Method request body before transformations$",event):
            varible_info = self.mrbbt(args)
            #print("MRBBT")
        elif re.match("^Endpoint request URI$",event):
            varible_info = self.eru(args)
            #print("ERU")
        elif re.match("^Endpoint request headers$",event):
            varible_info = self.ereqh(args)
            #print("EREQH")
        elif re.match("^Endpoint request body after transformations$",event):
            varible_info = self.erbat(args)
            #print("ERBAT")
        elif re.match("^Sending request",event):
            varible_info = self.sr(args)
            #print("SR")
        elif re.match("^Received response",event):
            varible_info = self.rr(args)
            #print("RR")
        elif re.match("^Endpoint response headers$",event):
            varible_info = self.eresh(args)
            #print("ERESH")
        elif re.match("^Endpoint response body before transformations$",event):
            varible_info = self.erbbt(args)
            #print("ERBBT")
        elif re.match("^Method response body after transformations$",event):
            varible_info = self.mrbat(args)
            #print("MRBAT")
        elif re.match("^Method response headers$",event):
            varible_info = self.mresh(args)
            #print("MRESH")
        elif re.match("^Successfully completed execution$",event):
            varible_info = self.sce(args)
            #print("SCE")
        elif re.match("^Method completed with status$",event):
            varible_info = self.mcws(args)
            #print("MCWS")
        else:
            #print('+-+-+-+-+-+-+-+-+-+ Not catched +-+-+-+-+-+-+-+-+-+-+')
            pass
        #print('---------> date match <----------')
        return event

    def line_processor(self, line):
        #print('#####################################')
        #print('line', line)
        substrings = line.split()
        if len(substrings) > 0:
            #print(substrings[0].decode('utf-8'))
            if re.match("^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])", substrings[0].decode('utf-8')):
                string_date = substrings[0].decode('utf-8')
                request_reference = substrings[1].decode('utf-8').replace(" ", "").replace("(", "").replace(")","")
                main_bytes_array = substrings[2:]
                main_decoded_array = [element.decode('utf-8') for element in main_bytes_array]
                main_string = ' '.join(main_decoded_array)
                args = [string_date, request_reference, main_string]
                event = self.event_processor(args)
            elif re.match(".*<.*>.*", line.decode('utf-8')):
                #print('tag match')
                pass
            elif re.match('.*".*":.*|\s*}.*', line.decode('utf-8')):
                #print('json match')
                pass
            else:
                #print(line.hex())
                print('not match')
                
def lambda_handler(event, context):
    substrings_array = []
    gateway = APIGateway()
    for gzip_file_name in glob.glob("production_exportedlogs/*"):
        with open(gzip_file_name, 'rb') as f:
            if gzip_file_name.split('/')[-1] != '0':
                file = gzip.GzipFile(fileobj=f)
                for line in file:
                    gateway.line_processor(line)
    #print(gateway.request_data_dictionary)

    partners = {
        'E1NOHTB48L8cQ92SWtRLT2eQr3RvCr5H38eFvI4C': 'TREO',
        'uWZrHO7zHa9m2THvGuPs2aldG9DFpSiY6T7bZGNQ': 'BAMBA',
        'G3PzAGRvgyarxEgS5Aodb7nK7PL74GPU9dlRS0wB': 'CACAO',
        '7RkEtq5uk2V3FYAcHDB9s78U6BU6vJwObah6HcAlf': 'LANA'
    }

    store_products_endpoint = '/v1/store/products'
    store_orders_endpoint = '/v1/store/orders'
    customer_endpoint = '/v1/customer/[^/]*'
    customer_services_endpoint = '/v1/customer/.*/services'
    customer_sevice_cancel_endpoint = '/v1/customer/.*/services/.*/cancel'
    advisor_message_endpoint = '/v1/advisor/message'
    endpoints = [
        store_products_endpoint,
        store_orders_endpoint,
        customer_endpoint,
        customer_services_endpoint,
        customer_sevice_cancel_endpoint,
        advisor_message_endpoint
    ]
    aux = {
        'fullname': [],
        'cellphone': [],
        'email': [],
        'birthdate': [],
        'gender': [],
        'partner': [],
        'request_id': [],
        'request_reference': [],
        'request_arrive_at': [],
        'verify_init_at': [],
        'api_key': [],
        'verify_result': [],
        'verify_result_at': [],
        'start_request_at': [],
        'http_method': [],
        'resource_path': [],
        'api_key_id': [],
        'product': [],
        'customer': [],
        'payment_media_type_key': [],
        'payment_mediatype_value': [],
        'send_request_at': [],
        'response_status': [],
        'response_latency': [],
        'response_received': []
    }
    for request_reference in gateway.request_data_dictionary:
        
        # if 'api_key' in self.request_data_dictionary[request_reference]:
        #     print('****************************************************************')
        #     print(self.request_data_dictionary[request_reference])
        #     print(type(self.request_data_dictionary[request_reference]))
        
        fullname = None
        cellphone = None
        email = None
        birthdate = None
        gender = None
        request_id = gateway.request_data_dictionary[request_reference]['request_id']
        request_reference = gateway.request_data_dictionary[request_reference]['request_reference']
        request_arrive_at = gateway.request_data_dictionary[request_reference]['request_start_at']
        verify_init_at = None # No tiene si la verificacion falla **
        api_key = None # No tiene si la verificacion falla **
        partner = None
        verify_result = gateway.request_data_dictionary[request_reference]['verify_result']
        verify_result_at = gateway.request_data_dictionary[request_reference]['verify_result_at']
        start_request_at = None # No tiene si la verificacion falla **
        http_method = None # No tiene si la verificacion falla **
        resource_path = None # No tiene si la verificacion falla **
        api_key_id = None # No tiene si la api_key asociada a un plan **
        product = None # En store/product **
        customer = None # En store/product **
        payment_media_type_key = None # No tiene si no hay pago **
        payment_mediatype_value = None # No tiene si no hay pago **
        send_request_at = None # No tiene si la api_key asociada a un plan **
        response_status = gateway.request_data_dictionary[request_reference]['response_status']
        response_latency = None # No tiene si la api_key asociada a un plan **
        response_received = None # No tiene un caso de advisor/message
        
        if re.match('.*succeeded.*', verify_result):
            # print('Entra')
            if len(verify_result.split(' ')[7]) == 36:
                verify_init_at = gateway.request_data_dictionary[request_reference]['verify_init_at']
                api_key = gateway.request_data_dictionary[request_reference]['api_key']
                api_key_end = '.*' + api_key[-6:] + '$'
                for known_api_key in partners:
                    if re.match(api_key_end, known_api_key):
                        partner = partners[known_api_key]
                start_request_at = gateway.request_data_dictionary[request_reference]['start_request_at']
                http_method = gateway.request_data_dictionary[request_reference]['http_method']
                resource_path = gateway.request_data_dictionary[request_reference]['resource_path']
                api_key_id = gateway.request_data_dictionary[request_reference]['api_key_id']
                send_request_at = gateway.request_data_dictionary[request_reference]['send_request_at']
                response_latency = gateway.request_data_dictionary[request_reference]['response_latency']
        
        if 'response_received' in gateway.request_data_dictionary[request_reference]:
            response_received = gateway.request_data_dictionary[request_reference]['response_received']
        
        if 'resource_path' in gateway.request_data_dictionary[request_reference] and gateway.request_data_dictionary[request_reference]['resource_path'] == '/v1/store/orders':
            # print('---------------------------------------------------------------------------------------')
            method_request_body_before_transformations = gateway.request_data_dictionary[request_reference]['method_request_body_before_transformations']
            # print(method_request_body_before_transformations)
            # print(type(method_request_body_before_transformations))
            if re.match('{[\S]}', method_request_body_before_transformations):
                method_request_body_before_transformations = json.loads(method_request_body_before_transformations)
                customer = method_request_body_before_transformations['customer']
                products = method_request_body_before_transformations['products']
                fullname = customer['name']
                fullname += customer['lastName']
                fullname += customer['secondLastName']
                cellphone = customer['cellphone']
                email = customer['email']
                birthdate = customer['birthdate']
                gender = customer['gender']
                if 'paymentParams' in method_request_body_before_transformations:
                    payment_params = method_request_body_before_transformations['paymentParams']
                    media_type_key = payment_params['mediaTypeKey']
                    media_type_value = payment_params['mediaTypeValue']
                # print(method_request_body_defore_transformations)
                # print(type(method_request_body_defore_transformations))
            # print('---------------------------------------------------------------------------------------')
        aux['fullname'].append(str(fullname))
        aux['cellphone'].append(cellphone)
        aux['email'].append(email)
        aux['birthdate'].append(birthdate)
        aux['gender'].append(gender)
        aux['partner'].append(partner)
        aux['request_id'].append(request_id)
        aux['request_reference'].append(request_reference)
        aux['request_arrive_at'].append(request_arrive_at)
        aux['verify_init_at'].append(verify_init_at)
        aux['api_key'].append(api_key)
        aux['verify_result'].append(verify_result)
        aux['verify_result_at'].append(verify_result_at)
        aux['start_request_at'].append(start_request_at)
        aux['http_method'].append(http_method)
        aux['resource_path'].append(resource_path)
        aux['api_key_id'].append(api_key_id)
        aux['product'].append(product)
        aux['customer'].append(str(customer))
        aux['payment_media_type_key'].append(payment_media_type_key)
        aux['payment_mediatype_value'].append(payment_mediatype_value)
        aux['send_request_at'].append(send_request_at)
        aux['response_status'].append(response_status)
        aux['response_latency'].append(response_latency)
        aux['response_received'].append(response_received)

    df = pd.DataFrame(aux)

    df.to_sql(name='production_api_gateway',con=gateway.datalake_conn,if_exists='replace',index=False)
    
    shutil.rmtree("production_exportedlogs")

if __name__ == "__main__":
    lambda_handler(event={},context={})
    