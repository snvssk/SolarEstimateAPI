from google.cloud import bigquery
from google.oauth2 import service_account
from flask import request
import time,json,os

from google.cloud import storage
import base64
import urllib.parse
from pprint import pprint
import datetime


from Roofsize import Roofsize
from LatLong import LatLong
from MapBox import MapBox
from Solarenergy import Solarenergy

#Credentials to access Google Account
#Json Files are not committed to Git, Check with Dev
credentials = service_account.Credentials.from_service_account_file('data298-347103-eaa0e3e59658.json')

#BigQuery and Storage Client
project_id = 'data298-347103'
client = bigquery.Client(credentials= credentials,project=project_id)
storage_client = storage.Client(credentials=credentials, project=project_id)

#Upload To Google Cloud Storage
bucket = storage_client.get_bucket('solarestimation_images')


class Housetype:

    #Fetch House type infromation from County Database
    def post(self):
        print('call received')
        print(request)
        print(request.form)
        args = request.get_json()
        print(args)
        # Store User Uploaded image into mapbox images folder
        user_upload_filename = "useruplaoded_image_"+str(time.time())+".png"
        upload_path = "mapbox_images/"+user_upload_filename
        with open(upload_path, "wb") as fh:
            fh.write(base64.b64decode(args['roofImageFile']))

        address = args['address']
        city = args['city']
        state = args['state']
        zipcode = args['zipcode']
        energy_usage = args['energy_usage']
        member_count = args['member_count']
        
        return self.processinput(address,city,state,zipcode,energy_usage,member_count,upload_path)

    def get(self):
        print(request.args)
        print(urllib.parse.unquote(request.args['address']))
        args = request.args
        address = args['address']
        city = args['city']
        state = args['state']
        zipcode = args['zipcode']
        zipcode = args['zipcode']
        energy_usage = args['energy_usage']
        member_count = args['member_count']

        return self.processinput(address,city,state,zipcode,energy_usage,member_count)
        


    def processinput(self,address,city,state,zipcode,energy_usage,member_count,upload_path=''):

        #Response String
        address_result = {'Address': address, 'ZipCode': zipcode, 'City': city, 
                            'State': state, 'energy_usage':  energy_usage, 'member_count': member_count,
                            'Unit_Type': 'Single Family', 'County': 'Santa Clara', 'longitude': 0.0, 'latitude': 0.0}

        latlong = LatLong()
        mapbox = MapBox()
        roofsize = Roofsize()
        solarintensity = Solarenergy()

        latitude,longitude = latlong.get(address_string=address+city+state+zipcode)
        if(latitude!=0 and longitude!=0):
            address_result['longitude'] = longitude
            address_result['latitude'] = latitude

            if(upload_path==''):
                #Calling Mapbox API
                image_results = json.loads(mapbox.get(longitude,latitude))
                #print(type(image_results))
                print(image_results)
                public_url_input_img = image_results['public_url_img']


                #Segment and Roofsize calculation for mapbox image
                roof_results = json.loads(roofsize.get('mapbox_images/'+image_results['mapbox_downloaded_filename']))
                #print(roof_results)
                #print(type(roof_results))
                
            else:
                #Segment and Roofsize calculation for image uploaded by the user
                roof_results = json.loads(roofsize.get(upload_path))
                #print(roof_results)
                #print(type(roof_results))
                
                #User uploaded image to cloud storage
                blob = bucket.blob('user_uploads/'+os.path.basename(upload_path))
                blob.upload_from_filename(upload_path)
                public_url_input_img = "https://storage.googleapis.com/solarestimation_images/user_uploads/"+os.path.basename(upload_path)
                

            #Segmentation and Roof Size 
            segmented_blob = bucket.blob("segmented_images/"+os.path.basename(roof_results['segmented_image']))
            segmented_blob.upload_from_filename(roof_results["segmented_image"])
            segmented_public_url_img = "https://storage.googleapis.com/solarestimation_images/segmented_images/"+os.path.basename(roof_results['segmented_image'])
            
            address_result['roof_size'] = roof_results['roof_size']
            address_result['roof_type'] = roof_results['roof_type']
            address_result['panel_area'] = roof_results['panel_area']
            address_result['panel_count'] = roof_results['panel_count']
            address_result['segmented_image_url'] = segmented_public_url_img
            address_result['roof_image_url'] = public_url_input_img
            address_result['status'] = 'OK'
            self.storeUserRequests(address_result)

            county_data_response = self.countyData(address,zipcode,city)
            if(county_data_response['status']!='failed'):
                if(county_data_response['Unit_Type']=='Commercial'):
                    address_result['Unit_Type'] = "Single Family"
                else:
                    address_result['Unit_Type'] = county_data_response['Unit_Type']
                address_result['County'] = county_data_response['County']

            solarintensity_estimates =  json.loads(solarintensity.get(address_result['City']) )
            if(solarintensity_estimates['status']=='ok'):
                address_result['solarintensity'] =  solarintensity_estimates['median_solar_intensity']
            else:
                address_result['solarintensity'] = -1.0
            

        else:
            address_result={'status': 'failed', 'reason': 'Address Not Found'}

        print(address_result)
        

        return json.dumps(str(address_result))

   
    def countyData(self,address,zipcode,city):
        

        #BigQuery Lookup for Address
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
        if(housetype_result.result().total_rows>0):
            housetype_records = [dict(row) for row in housetype_result]
            print(housetype_records[0])
            county_data = {'Unit_Type': housetype_records[0]['Unit_Type'], 'County' : 'Santa Clara' ,'status': 'OK'}

        else:
            county_data = {"status": "failed", "reason" :"Address Not Found"}
        
        return county_data

    def storeUserRequests(self,estimation_result):
        ct = datetime.datetime.now()
        ts = ct.timestamp()
        rows_to_insert = [
            {"request_time" : ts, "user_house_address": estimation_result['Address'], "user_city" : estimation_result['City'],
             "user_zipcode" : int(estimation_result['ZipCode']), "user_state": estimation_result['State'], 
             "user_family_member_count": int(estimation_result['member_count']), "user_energy_usage": int(estimation_result['energy_usage']),
              "latitude": estimation_result['latitude'], "longitude" :estimation_result['longitude'], "roof_size_estimate" : float(estimation_result['roof_size']),
              "roof_type_estimate" :  estimation_result['roof_type'],"roof_panel_area_estimate": float(estimation_result['panel_area']),
              "roof_panel_count_estimate":  int(estimation_result['panel_count']), "user_roof_image_url": estimation_result['roof_image_url'],
              "segmented_roof_image_url": estimation_result['segmented_image_url'],"unit_type_estimate": estimation_result['Unit_Type'] }
        ]
        table_id = "data298-347103.projectReports.SolarEstimationRequests"
        
        print("BigQuery Insert")
        print(rows_to_insert)
        try:
            userrequest_insertion_result = client.insert_rows_json(table_id, rows_to_insert)
            print(userrequest_insertion_result)
            #print(userrequest_insertion_result.errors)
            #pprint(vars(userrequest_insertion_result))
        except:
            pprint(vars(userrequest_insertion_result))
        
        return 0

    


    
       



