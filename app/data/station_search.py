import json
import os

import pandas as pd
import requests
from dotenv import load_dotenv

from app.data.settings import BASE_URI

load_dotenv()


class StationSearch:
    def __init__(self, key: str, station: str = None):
        self._base_url = "https://mw.buoybay.noaa.gov/api/v1/"
        self.station = station
        self.key = key

    def _grab_station_data(self):
        if not self.station:
            raise ValueError("Station ID must be provided")
        try:
            response = requests.get(f"{self._base_url}json/station/{self.station}/?key={self.key}")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching data: {e}")
            return None

    def _grab_all_station_data(self):
        try:
            response = requests.get(f"{self._base_url}json/station?key={self.key}")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching data: {e}")
            return None


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
    variable['actualName']
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
print(dict(zip(report_name, measurements)))

