from google.cloud import aiplatform
from google.oauth2 import service_account
from sklearn.preprocessing import StandardScaler
from flask import request
import numpy as np
import pandas as pd
import json

credentials = service_account.Credentials.from_service_account_file('data298-347103-eaa0e3e59658.json')

project_id = 'data298-347103'
PROJECT_NUMBER='586683398823'
ENDPOINT_ID='7642485422345420800'
endpoint_name=f"projects/"+PROJECT_NUMBER+"/locations/us-east1/endpoints/"+ENDPOINT_ID



df = pd.read_csv('data/all_2021test_transformed.csv')
df = df.loc[(df['Hour'].isin([7, 10, 13, 16, 19])) & (df['Minute'] == 0)]
testdata = df.drop(columns='Unnamed: 0')
testdata_final = testdata.dropna()



input = testdata_final.drop(['GHI'],axis =1)
#print(input.loc[10])

sc = StandardScaler()
input_nor_test = sc.fit_transform(input)
#x = input_nor_test[2].astype(np.float32).tolist()
#print(x)

class Solarenergy:
    def get(self):
        args = request.args
        endpoint=aiplatform.Endpoint(endpoint_name=endpoint_name,credentials=credentials)
        energy_result = []
        for i in range(30):
            
            x = input_nor_test[i].astype(np.float32).tolist()
            print(x)
            prediction = endpoint.predict(instances=[x]).predictions
            energy_result.append(prediction[0])

        return json.dumps(energy_result)


