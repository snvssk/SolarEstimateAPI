from google.cloud import bigquery
import json

client = bigquery.Client()


class Housetype:
    def get(self):
        housetype_sql = "SELECT * FROM `data298-347103.County_Addresses.COUNTY_ADDRESS_DATA` LIMIT 10"

        query_housetype = client.query(housetype_sql) 
        housetype_records = [dict(row) for row in query_housetype]
        json_obj = json.dumps(str(housetype_records))
        return json_obj