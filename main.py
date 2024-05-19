import os
from dotenv import load_dotenv
import requests

load_dotenv()

base_uri = "https://mw.buoybay.noaa.gov/api/v1/"
response = requests.get(f"{base_uri}json/station?key={os.getenv('API_KEY')}")

API_Data = response.json()
# print(response.json())

# Print json data using loop 
for key in API_Data:{ 
    print(key,":", API_Data[key]) 
}