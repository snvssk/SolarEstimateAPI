from google.cloud import bigquery
from google.oauth2 import service_account
from flask import request
credentials = service_account.Credentials.from_service_account_file('data298-347103-eaa0e3e59658.json')

import json
project_id = 'data298-347103'
client = bigquery.Client(credentials= credentials,project=project_id)


class Housetype:
    def get(self):
        args = request.args
        
        #args = { 'address': '1644 STEMEL WAY', 'city': 'Milpitas','state': 'California','zipcode': '95035','family-size': '3','energy-bill': '0'}
        print(args)
        address = args['address']
        city = args['city']
        state = args['state']
        zipcode = args['zipcode']
        housetype_sql = """SELECT * FROM `data298-347103.County_Addresses.COUNTY_ADDRESS_DATA` 
                            WHERE Address=@address and ZipCode=@zipcode and City=@city LIMIT 1"""


        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("address", "STRING", address),
                bigquery.ScalarQueryParameter("city", "STRING", city),
                bigquery.ScalarQueryParameter("zipcode", "STRING", zipcode),
            ]
        )
        
        housetype_result = client.query(housetype_sql,job_config=job_config) 
        address_result = '{"result":"Address Not Valid"}'
        if(housetype_result.result().total_rows>0):
            housetype_records = [dict(row) for row in housetype_result]
            address_result = json.dumps(str(housetype_records))

        return address_result


