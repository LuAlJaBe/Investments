from pathlib import Path
import requests
import sys
import os
import environ
from datetime import datetime
from pdb import set_trace as bp

class CampaignsPreparer():
    def __init__(self, data):
        self.get_data(data)
        self.set_credentials()
        self.max_request_customers = 100
        self.config_campaigns()
        self.list_customers_url_base = "https://api.landbot.io/v1/customers/?archived=true&opt_in=true&limit={}&offset={}"
        self.field_name = 'current_campaign'
        self.campaign_data = {
            "type": "string",
            "extra": {},
            "value": ""
        }
        self.customer_change_field_url_base = 'https://api.landbot.io/v1/customers/{}/fields/{}/'
        self.ids_set = set(())
        self.excluded_list = []
        print('ids type: ', type(self.ids_set))
        
    def get_data(self,data):
        self.data = {'campaign_' + str(i):dictionary for i ,dictionary in enumerate(data)}
    
    def set_credentials(self):
        env = environ.Env()
        BASE_DIR = Path(__file__).resolve().parent.parent
        environ.Env.read_env(os.path.join(BASE_DIR, 'bi','.env'))
        LANDBOT_API_TOKEN = env('LANDBOT_API_TOKEN')
        self.authorization = "Token " + LANDBOT_API_TOKEN
        self.headers = {"Authorization": self.authorization, "Content-Type": "application/json"}
    
    def config_campaigns(self):
        audiences = []
        breakpoint = 0
        for key in self.data:
            campaign = self.data[key]
            campaign['lower_breakpoint'] = breakpoint
            audience = campaign['audience']
            breakpoint += audience
            campaign['upper_breakpoint'] = breakpoint
            audiences.append(campaign['audience'])
        self.customers_wanted = sum(audiences)
    
    def request_customers(self, customers_wanted, run_time):
        offset = str(run_time * self.max_request_customers)
        list_customers_url = self.list_customers_url_base.format(customers_wanted, offset)
        customers_response = requests.get(list_customers_url, headers=self.headers)
        if customers_response.status_code == 200:
            self.customers = customers_response.json()['customers']
        else:
            print('Something went wrong when getting customers')
    
    def get_customers_ids(self):
        self.ids = []
        for customer in self.customers:
            if 'current_campaign' in customer and customer['current_campaign'] not in self.excluded_list:
                self.ids.append(customer['id'])
            elif 'current_campaign' not in customer:
                self.ids.append(customer['id'])
        self.ids = set(self.ids)
            
    def add_new_ids_to_ids_set(self):
        self.ids_set.update(self.ids)
        print('The lenght of ids_set is: ', len(self.ids_set))
        
    def divide(self):
        self.complete_run_times = self.customers_wanted // self.max_request_customers
        self.remainder = self.customers_wanted % self.max_request_customers
    
    def check_remainder(self):
        self.remainder_different_from_zero = False
        if self.remainder != 0:
            self.remainder_different_from_zero = True
    
    def get_customers_ids_set(self):
        print('Se va a hacer para ', self.run_times)
        for run_time in range(self.run_times):
            print(run_time)
            customers_wanted = self.max_request_customers
            if self.remainder_different_from_zero and run_time == self.run_times - 1:
                customers_wanted = self.remainder
                print('La última y empezamos')
            self.request_customers(customers_wanted, run_time)
            self.get_customers_ids()
            self.add_new_ids_to_ids_set()
    
    def get_campaign_name(self, user_number):
        for key in self.data:
            campaign = self.data[key]
            str_date = campaign['schedule'].strftime("%Y%m%d_%H%M")
            if campaign['lower_breakpoint'] <= user_number < campaign['upper_breakpoint']:
                self.campaign_data['value'] = campaign['campaign_name'] + '_' + str_date
    
    def segment_customers(self):
        user_number = 0
        for customer_id in self.ids_set:
            try:
                self.get_campaign_name(user_number)
                customer_change_field_url = self.customer_change_field_url_base.format(customer_id,self.field_name)
                print(user_number)
                print(customer_change_field_url)
                response = requests.put(customer_change_field_url, headers=self.headers, json=self.campaign_data)
                print('put')
                if response.status_code == 200:
                    user_number += 1
                elif response.status_code == 404:
                    response = requests.post(customer_change_field_url, headers=self.headers, json=self.campaign_data)
                    print('post')
                    if response.status_code == 200:
                        user_number += 1
                    else:
                        print(response)
            except:
                pass 
    
    def main(self):
        self.divide()
        self.run_times = self.complete_run_times
        self.check_remainder()
        if self.remainder_different_from_zero:
            self.run_times += 1
        self.get_customers_ids_set()
        self.segment_customers()

if __name__ == '__main__':
    if len(sys.argv) > 1 and (sys.argv[1] == 'historical' or sys.argv[1] == 'hist'):
        mode = 'historical'
    campaign = CampaignsPreparer(750)
    campaign.main()