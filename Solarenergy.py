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
ENDPOINT_ID='5439662254607826944'
endpoint_name=f"projects/"+PROJECT_NUMBER+"/locations/us-east1/endpoints/"+ENDPOINT_ID



df = pd.read_csv('data/cupertino_transformed_combined.csv')
testdata = df.drop(columns='Unnamed: 0')
testdata_final = testdata.dropna()
df['Hour'] = df['Hour'] + df['Minute'] / 60
data_trimmed = df.drop(['Minute', 'Unnamed: 0'],axis =1)
#print(data_trimmed)

input = data_trimmed.drop(['GHI', 'Location'],axis =1)


sc = StandardScaler()
input_nor_test = sc.fit_transform(input)
x = input_nor_test[2].astype(np.float32).tolist()
#print(x)

class Solarenergy:
    def get(self):
        args = request.args
        endpoint=aiplatform.Endpoint(endpoint_name=endpoint_name,credentials=credentials)
        energy_result = endpoint.predict(instances=[x]).predictions

        return json.dumps(energy_result[0])


