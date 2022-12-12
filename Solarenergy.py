from google.cloud import aiplatform
from google.oauth2 import service_account
from sklearn.preprocessing import StandardScaler
from datetime import datetime
from flask import request
import numpy as np
import pandas as pd
import json,statistics

project_id = 'data298-347103'
PROJECT_NUMBER='586683398823'
ENDPOINT_ID='8663324794130792448'
endpoint_name=f"projects/"+PROJECT_NUMBER+"/locations/us-east1/endpoints/"+ENDPOINT_ID


credentials = service_account.Credentials.from_service_account_file('data298-347103-eaa0e3e59658.json')
endpoint=aiplatform.Endpoint(endpoint_name=endpoint_name,credentials=credentials)

df = pd.read_csv('data/all_2021test_transformed.csv')
df = df.loc[(df['Hour'].isin([7, 10, 13, 16, 19])) & (df['Minute'] == 0)]
sc = StandardScaler()

city_weatherstation_map = {"ALVISO" : 144994,"CAMPBELL" : 144395,"COYOTE" : 147404,"CUPERTINO" : 143196,"GILROY" : 149835,
                            "HOLLISTER" : 152283,"LOS ALTOS" : 142002,"LOS ALTOS HILLS" : 141410,"LOS GATOS" : 142002,
                            "MILPITAS" : 144992,"MONTE SERENO" : 143797,"MORGAN HILL" : 148616,"MOUNTAIN VIEW" : 142002,
                            "PALO ALTO" : 141408,"PORTOLA VALLEY" : 140248,"SAN JOSE" : 144994,"SAN MARTIN" : 149224,
                            "SANTA CLARA" : 144393,"SARATOGA" : 143198,"Stanford" : 140828,"SUNNYVALE" : 143195,"WATSONVILLE" : 147412}

class Solarenergy:
    def get(self,city):
        if(city.upper() in city_weatherstation_map.keys()):
            today = datetime.now()
            lookup_month = datetime.strftime(today, '%-m')
            station_id = city_weatherstation_map[city.upper()]
            #print(station_id)
            #print(float(lookup_month))
            city_df = df.loc[(df['Location'] == float(station_id)) & (df['Month'] == float(lookup_month))]
            city_df = city_df.drop(['GHI','Unnamed: 0'],axis =1)
            city_df_final = city_df.dropna()
            print(city_df.head())
            city_df_input = sc.fit_transform(city_df_final)

            x = city_df_input[0].astype(np.float32).tolist()
            #print(x)            
            #print("No.of rows: " +str(len(city_df.index)))
            
            energy_estimations = []
            energy_query_inputs =[]
            for i in range(len(city_df.index)):
                
                x = city_df_input[i].astype(np.float32).tolist()
                #print(x)
                energy_query_inputs.append(x)

            prediction = endpoint.predict(instances=energy_query_inputs).predictions
            #energy_result.append(prediction[0])
            #print(prediction)
            for energy_result in prediction:
                #print(energy_result[0])
                energy_estimations.append(energy_result[0])
            #print(statistics.median(energy_estimations))
            return json.dumps({"status": "ok","median_solar_intensity": statistics.median(energy_estimations), "avg_solar_intensity": statistics.mean(energy_estimations)} )
        else:
            return json.dumps({"status": "failed", "reason": "Not found"})


#solar_energy_obj = Solarenergy()
#print(solar_energy_obj.get('San Jose'))
