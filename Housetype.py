from google.cloud import bigquery
from google.cloud import storage
from google.oauth2 import service_account
from flask import request
import requests,json
import time
import json


#Credentials to access Google Account, Google Maps, Map box API
#Json Files are not committed to Git, Check with Dev
credentials = service_account.Credentials.from_service_account_file('data298-347103-eaa0e3e59658.json')
f = open ('maps_api_key.json', "r")
maps_key_json = json.loads(f.read())
google_maps_api_key = maps_key_json['google_maps_api_key']
map_box_api_key = maps_key_json['map_box_api_key']

#External API URLs
GOOGLE_MAPS_API_URL = 'https://maps.googleapis.com/maps/api/geocode/json'
MAP_BOX_API_URL = 'https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/'


#BigQuery and Storage Client
project_id = 'data298-347103'
client = bigquery.Client(credentials= credentials,project=project_id)
storage_client = storage.Client(credentials=credentials, project=project_id)


class Housetype:

    #Fetch House type infromation from County Database
    def get(self):
        args = request.args
    
        address = args['address']
        city = args['city']
        state = args['state']
        zipcode = args['zipcode']

        #Response String
        address_result = {'Address': args['address'], 'ZipCode': '95035', 'City': args['city'], 
                            'State': args['state'], 'Unit_Type': 'Unknown', 'County': 'Unknownx', 
                            'longitude': 0.0, 'latitude': 0.0, 
                            'roof_image': ''}

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
        address_result = '{"result":"Address Not Valid"}'

        if(housetype_result.result().total_rows>0):
            housetype_records = [dict(row) for row in housetype_result]
            latitude,longitude = self.latlong(address_string=address+city+state+zipcode)
            housetype_records[0]['longitude'] = longitude
            housetype_records[0]['latitude'] = latitude
            image_url = self.mapbox(longitude,latitude)
            housetype_records[0]['roof_image'] = image_url
            address_result = json.dumps(str(housetype_records))
            
        return address_result

    #Fetch Latitude and Longitude 
    def latlong(self,address_string):
        
        #Parameters for Google Maps API for Latitude and Longitude conversion
        params = {
            'address': address_string,
            'sensor': 'false',
            'region': 'india',
            'key': google_maps_api_key 
        }

        # Calling Google Maps API 
        req = requests.get(GOOGLE_MAPS_API_URL, params=params)
        res = req.json()
        #print(res)


        # Use the first result
        result = res['results'][0]

        #Create a Dictionary for the result
        geodata = dict()
        geodata['lat'] = result['geometry']['location']['lat']
        geodata['lng'] = result['geometry']['location']['lng']
        geodata['address'] = result['formatted_address']
        #print('{address}. (lat, lng) = ({lat}, {lng})'.format(**geodata))
        return geodata['lat'],geodata['lng']

    #Map Box API call for getting Image   
    def mapbox(self,longitude,latitude):

        #Map Box API Params
        zoom_level = '19' 
        bearing = '47' # rotating map
        pitch = '0' # tilting map
        img_size = '256x256@2x'
        static_params = [str(longitude),str(latitude),zoom_level,bearing,pitch]

        params = {
            'access_token': map_box_api_key 
        }
        
        # Get the Satellite Image from Mapbox API
        req = requests.get(MAP_BOX_API_URL+",".join(static_params)+"/"+img_size, params=params)
        

        # Write in a local folder before upload
        mapbox_downloaded_filename = "satellite_image_"+str(time.time())+".png"
        local_folder_name = "mapbox_images/"
        file = open(local_folder_name +mapbox_downloaded_filename, "wb")
        file.write(req.content)
        file.close()

        #Upload To Google Cloud Storage
        bucket = storage_client.get_bucket('solarestimation_images')
        blob = bucket.blob('mapbox_downloads/'+mapbox_downloaded_filename)
        blob.upload_from_filename(local_folder_name +mapbox_downloaded_filename)
        public_url_img = "https://storage.googleapis.com/solarestimation_images/mapbox_downloads/"+mapbox_downloaded_filename
        return public_url_img
       



