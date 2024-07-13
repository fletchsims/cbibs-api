import json
import os

import pandas as pd
import requests
from dotenv import load_dotenv

from app.data.settings import BASE_URI

load_dotenv()

# response = requests.get(f"{BASE_URI}json/station/AN?key={os.getenv('CBIBS_API_KEY')}")

# API_Data = response.json()

with open(os.getenv('SAMPLE_JSON_PATH')) as sample_data:
    sample = sample_data.read()

# print(json.loads(sample)['stations']['stationShortName'])

df = pd.json_normalize(json.loads(sample), 'stations')['variable']


# print(list(df))
# print(df['variable'])


def parse_json(data):
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = parse_json(value)
        else:
            result[key] = value
    return result


tmp = parse_json(json.loads(sample))

report_name = tmp['stations'][0]['variable'][1]['reportName']

actual_names = [
    variable['actualName']
    for station in tmp['stations']
    for variable in station['variable']
]
actual_names.insert(0, 'time_utc')
measurements = [
    msr['value']
    for station in tmp['stations']
    for variable in station['variable']
    for msr in variable['measurements']
]
time_utc = list({
    msr['time']
    for station in tmp['stations']
    for variable in station['variable']
    for msr in variable['measurements']
})
measurements.insert(0, time_utc[0])

print(actual_names)
print(measurements)
print(time_utc)
# print(report_name)
