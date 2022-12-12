
import json,requests

#Credentials to access  Google Maps
#Json Files are not committed to Git, Check with Dev
f = open ('maps_api_key.json', "r")
maps_key_json = json.loads(f.read())
google_maps_api_key = maps_key_json['google_maps_api_key']

#External API URLs
GOOGLE_MAPS_API_URL = 'https://maps.googleapis.com/maps/api/geocode/json'
GOOGLE_MAPS_PLACE_URL = 'https://maps.googleapis.com/maps/api/place/details/json'

class LatLong:

 #Fetch Latitude and Longitude 
    def get(self,address_string):
        
        #Parameters for Google Maps API for Latitude and Longitude conversion
        params = {
            'address': address_string,
            'sensor': 'false',
            'region': 'india',
            'key': google_maps_api_key 
        }
        print(params)
        # Calling Google Maps API 
        req = requests.get(GOOGLE_MAPS_API_URL, params=params)
        res = req.json()
        print(res)

        if(res['status']=='OK'):
            # Use the first result
            result = res['results'][0]
            if(result['geometry']['location_type']=='ROOFTOP'):
                #Create a Dictionary for the result
                geodata = dict()
                geodata['lat'] = result['geometry']['location']['lat']
                geodata['lng'] = result['geometry']['location']['lng']
                geodata['address'] = result['formatted_address']
                print('{address}. (lat, lng) = ({lat}, {lng})'.format(**geodata))
                return geodata['lat'],geodata['lng']
            else:
                print("Not a Rooftop")
                print(result)
        
        return 0,0
    
#    def placedetails(self,placeid):



#latLong_obj = LatLong()
#print(latLong_obj.get('265 Baja rose St, Milpitas, CA, 95035'))
#print(latLong_obj.get('301 Ranch Dr, Milpitas, CA 95035'))
#print(latLong_obj.get('Ranch Dr, Milpitas, CA 95035'))
