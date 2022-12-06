
import json,requests,os
from google.oauth2 import service_account
from google.cloud import storage
import time

#Credentials to access  Map box API
#Json Files are not committed to Git, Check with Dev
f = open ('maps_api_key.json', "r")
maps_key_json = json.loads(f.read())

map_box_api_key = maps_key_json['map_box_api_key']
#External API URLs
MAP_BOX_API_URL = 'https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/'

project_id = 'data298-347103'
credentials = service_account.Credentials.from_service_account_file('data298-347103-eaa0e3e59658.json')
storage_client = storage.Client(credentials=credentials, project=project_id)

class MapBox:
#Map Box API call for getting Image   
    def get(self,longitude,latitude):

        #Map Box API Params
        zoom_level = '19' 
        bearing = '47' # rotating map
        pitch = '0' # tilting map
        img_size = '256x256@2x'
        img_size = '256x256'
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

        response_json = {'public_url_img': public_url_img, 'mapbox_downloaded_filename': mapbox_downloaded_filename }
        print(response_json)
     
        return json.dumps(response_json)