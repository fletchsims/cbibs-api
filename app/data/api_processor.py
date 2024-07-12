import os

import requests
from dotenv import load_dotenv

from app.data.settings import BASE_URI

load_dotenv()

response = requests.get(f"{BASE_URI}json/station/AN?key={os.getenv('CBIBS_API_KEY')}")

API_Data = response.json()
print(response.json())
