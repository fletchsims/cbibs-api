import json
import os

import pandas as pd
import requests
from dotenv import load_dotenv

from app.data.settings import BASE_URI

load_dotenv()

# response = requests.get(f"{BASE_URI}json/station/AN?key={os.getenv('CBIBS_API_KEY')}")

# API_Data = response.json()

met_remap = {

}
ocean_remap = {
    'time_utc': 'time_utc',
    'Current Average Speed': 'current_average_speed',
    'Current Average Direction': 'current_average_direction',
    'Latitude': 'latitude',
    'Longitude': 'longitude',
    'Wave Direction': 'wave_direction',
    'Maximum Wave Height': 'maximum_wave_height',

}
with open(os.getenv('SAMPLE_JSON_PATH')) as sample_data:
    sample = sample_data.read()


def parse_json(data):
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = parse_json(value)
        else:
            result[key] = value
    return result


tmp = parse_json(json.loads(sample))

# report_name = tmp['stations'][0]['variable'][1]['reportName']

report_name = [
    variable['reportName']
    for station in tmp['stations']
    for variable in station['variable']
]
report_name.insert(0, 'time_utc')
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
api_data = dict(zip(report_name, measurements))

print(dict(zip(report_name, measurements)))
# print(report_name)
